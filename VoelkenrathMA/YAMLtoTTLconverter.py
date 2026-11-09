# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "linkml>=1.9,<2",
#     "pyyaml>=6",
# ]
# ///
"""
YAMLtoTTLconverter
==================

Converts the simulation YAML files (one per DWSIM simulation) into RDF/Turtle,
using the LinkML schema ``linkml/PFR_Scheme.yaml``, and sorts every simulation
into its own folder:

    <output>/<input folder name>/<simulation name>/
        <simulation name>.dwxmz   DWSIM simulation file
        <simulation name>.yaml    original simulation YAML
        <simulation name>.ttl     generated RDF (Turtle)

Knowledge graph per simulation (all named individuals):

    <sim>  a reac4cat:Methanation              reaction conditions, results, file references
      reac4cat:hasInitialMixture  <sim>_Feed               a Mixture  (composition, molar flows)
      reac4cat:hasProduct         <sim>_Product            a Mixture
      afo:hasSeparatorGasOutlet   <sim>_SeparatorGas       a Mixture  (only with downstream)
      afo:hasSeparatorLiquidOutlet <sim>_SeparatorLiquid   a Mixture  (only with downstream)
      afo:hasReactor              <sim>_Reactor            a Reactor  (geometry, catalyst)
      afo:hasReactionMechanism    <sim>_ReactionMechanism  -> afo:hasReactionStep <sim>_Reaction_<id>
    <mixture>  reac4cat:hasComponent  reac4cat:Sub_CO2 ...  (substance individuals of MV-Onto.owl)

Every TTL also declares the properties, classes and substance individuals it uses
(owl:ObjectProperty / owl:DatatypeProperty / owl:Class / owl:NamedIndividual), so that
Protege and owlready2 treat them as properties and not as annotations, even if the file
is loaded on its own. The axial profiles are not converted; they stay in the YAML,
which is referenced via rdfs:comment.

Pipeline per simulation:
    1. read the YAML (list of single-key dicts, as written by the simulation scripts)
    2. map it onto the schema class ``MethanationSimulation``
    3. validate the instance against the schema (closed: unknown properties are errors)
    4. serialize it to Turtle with the LinkML RDF dumper (+ declarations), re-parse as a check
    5. copy (or move, with --move) the .dwxmz/.yaml and write the .ttl

Usage (uv installs the dependencies automatically, see header):
    uv run YAMLtoTTLconverter.py linkml/NewReaction_01
    uv run YAMLtoTTLconverter.py linkml/NewReaction_01 linkml/NewReaction_01_ --move
    uv run YAMLtoTTLconverter.py --help
"""

from __future__ import annotations

import argparse
import csv
import logging
import shutil
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, URIRef

from linkml.generators.pythongen import PythonGenerator
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import rdflib_dumper

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_DIR / "linkml" / "PFR_Scheme.yaml"
DEFAULT_OUTPUT = SCRIPT_DIR / "linkml" / "Simulations"
DEFAULT_BASE_URI = "http://example.com/data/methanation/"
TARGET_CLASS = "MethanationSimulation"
COMPOUND_ENUM = "Compound"

# YAML key -> schema slot
REACTOR_SLOTS = {
    "calculation_mode": "has_reactor_calculation_mode",
    "reactive_volume": "has_reactive_volume",
    "tube_length": "has_reactor_tube_length",
    "tube_diameter": "has_reactor_tube_diameter",
    "num_tubes": "has_reactor_number_of_tubes",
    "catalyst_loading": "has_catalyst_loading",
    "catalyst_particle_diameter": "has_catalyst_particle_diameter",
    "catalyst_void_fraction": "has_catalyst_void_fraction",
}
REACTION_SLOTS = {
    "reaction_equation": "has_reaction_equation",
    "K_1": "has_kinetic_parameter_k1",
    "K_2": "has_kinetic_parameter_k2",
    "K_3": "has_kinetic_parameter_k3",
    "br": "has_kinetic_parameter_br",
    "EA": "has_activation_energy",
    "beta": "has_temperature_exponent",
    "S0": "has_sticking_coefficient",
    "A_cm_units": "has_pre_exponential_factor",
    "epsilon": "has_coverage_parameter_epsilon",
    "mu": "has_coverage_parameter_mu",
}
STRING_SLOTS = {"has_reactor_calculation_mode", "has_reaction_equation"}
INTEGER_SLOTS = {"has_reactor_number_of_tubes", "has_reaction_id"}

# Top-level YAML keys that are mapped / deliberately not converted (profiles).
# Every other key (except concentration profiles named after a substance) is an error,
# so no information is lost silently.
MAPPED_KEYS = {
    "Reaction_Type", "Mixture", "Reactor", "ChemicalReaction", "Inlet", "Outlet",
    "Outlet Composition", "Sep_Gas Composition", "Sep_Liquid Composition", "hasDownstream",
    "Turnover", "Yield", "Selectivity", "Selectivity_normed",
}
PROFILE_KEYS = {"Coordinates", "Temperature", "Pressure"}

log = logging.getLogger("YAMLtoTTL")


class ConversionError(Exception):
    """Raised when a simulation YAML cannot be mapped onto the schema."""


# ---------------------------------------------------------------------------
# Helpers for the YAML structure written by the simulation scripts
# ---------------------------------------------------------------------------
def to_decimal(value: Any) -> Decimal:
    """Numbers are written as xsd:decimal (as in MV-Onto.owl), without float rounding."""
    if isinstance(value, bool):
        raise ConversionError(f"expected a number, got boolean {value!r}")
    try:
        # repr() keeps the shortest exact representation of a float;
        # strings cover values PyYAML does not parse as numbers (e.g. "1E-02")
        number = Decimal(repr(value) if isinstance(value, float) else str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ConversionError(f"expected a number, got {value!r}") from exc
    if not number.is_finite():
        raise ConversionError(f"number is not finite: {value!r}")
    return number


def convert(slot: str, value: Any) -> Any:
    if slot in STRING_SLOTS:
        return str(value)
    if slot in INTEGER_SLOTS:
        number = to_decimal(value)
        if number != number.to_integral_value():
            raise ConversionError(f"expected an integer for '{slot}', got {value!r}")
        return int(number)
    return to_decimal(value)


def put(target: dict, slot: str, value: Any) -> None:
    if slot in target:
        raise ConversionError(f"value for '{slot}' is defined twice")
    target[slot] = convert(slot, value)


def single(section: Any, name: str) -> dict:
    """Sections are stored as a list with exactly one dict: ``- Reactor: [ {...} ]``."""
    if isinstance(section, dict):
        return section
    if isinstance(section, list) and len(section) == 1 and isinstance(section[0], dict):
        return section[0]
    raise ConversionError(f"section '{name}' is not a single mapping")


def pairs(section: Any, name: str) -> list[tuple[str, Any]]:
    """``[[CO2, 0.04], [H2, 0.05]]`` -> ``[(CO2, 0.04), (H2, 0.05)]``.
    A flat ``[Y_CH4, 0.0017]`` (as used for 'Yield') is accepted as one pair."""
    if (isinstance(section, list) and len(section) == 2
            and isinstance(section[0], str) and not isinstance(section[1], (list, dict))):
        section = [section]
    if not isinstance(section, list):
        raise ConversionError(f"section '{name}' is not a list")
    result = []
    for item in section:
        if not (isinstance(item, list) and len(item) == 2):
            raise ConversionError(f"section '{name}' contains an invalid pair: {item!r}")
        result.append((str(item[0]), item[1]))
    return result


def merge_top_level(raw: Any) -> dict:
    """The file is a list of single-key dicts -> merge them into one dict."""
    if not isinstance(raw, list):
        raise ConversionError("top level of the YAML is not a list")
    merged: dict[str, Any] = {}
    for entry in raw:
        if not (isinstance(entry, dict) and len(entry) == 1):
            raise ConversionError(f"top-level entry is not a single-key mapping: {entry!r}")
        key, value = next(iter(entry.items()))
        if key in merged:
            raise ConversionError(f"top-level key '{key}' occurs twice")
        merged[key] = value
    return merged


def snake(name: str) -> str:
    """'CarbonDioxide' -> 'carbon_dioxide' (part of the slot names)."""
    out = "".join(f"_{ch.lower()}" if ch.isupper() and i else ch.lower() for i, ch in enumerate(name))
    return out.replace(" ", "_")


# ---------------------------------------------------------------------------
# Mapping YAML -> schema instance (class MethanationSimulation)
# ---------------------------------------------------------------------------
class SimulationBuilder:
    def __init__(self, compounds: dict[str, tuple[str, str]]):
        # formula -> (slot name part, substance IRI), taken from the schema enum 'Compound'
        self.compounds = compounds

    def compound(self, formula: str) -> tuple[str, str]:
        if formula not in self.compounds:
            raise ConversionError(f"unknown compound '{formula}' (add it to enum '{COMPOUND_ENUM}' in the schema)")
        return self.compounds[formula]

    def mixture(self, iri: str, fractions: list[tuple[str, Any]], flows: list[tuple[str, Any]],
                total_flow: Any = None, temperature: Any = None) -> dict:
        mix: dict[str, Any] = {"iri": iri}
        components: list[str] = []
        if temperature is not None:
            put(mix, "has_temperature", temperature)
        for formula, value in fractions:
            part, substance = self.compound(formula)
            put(mix, f"has_molar_fraction_{part}", value)
            if mix[f"has_molar_fraction_{part}"] > 0 and substance not in components:
                components.append(substance)
        if total_flow is not None:
            put(mix, "has_total_molar_flow", total_flow)
        for formula, value in flows:
            part, substance = self.compound(formula)
            put(mix, f"has_molar_flow_{part}", value)
            if mix[f"has_molar_flow_{part}"] > 0 and substance not in components:
                components.append(substance)
        if components:
            mix["has_component"] = components
        return mix

    def build(self, raw: Any, sim_uri: str, dwsim_file: str | None, yaml_file: str) -> tuple[dict, list[str]]:
        """Returns the instance dict and a list of plausibility warnings."""
        data = merge_top_level(raw)
        warnings: list[str] = []
        sim: dict[str, Any] = {"iri": sim_uri}

        # --- reaction type = class of the simulation individual ---
        reaction_type = str(data.get("Reaction_Type", ""))
        if reaction_type != "Methanation":
            raise ConversionError(f"Reaction_Type '{reaction_type}' is not supported (schema class: Methanation)")

        mixture = single(data["Mixture"], "Mixture")
        substance_names = {str(e[1]) for e in mixture.get("substances", []) if isinstance(e, list) and len(e) == 2}
        unknown = [k for k in data if k not in MAPPED_KEYS | PROFILE_KEYS | substance_names]
        if unknown:
            raise ConversionError(f"unknown top-level keys: {unknown}")
        rest = set(mixture) - {"temperature", "pressure", "residence time", "mole_fraction", "substances"}
        if rest:
            raise ConversionError(f"unknown keys in 'Mixture': {sorted(rest)}")

        # --- reaction conditions (YAML: Mixture) ---
        temperature = mixture.get("temperature")
        if isinstance(temperature, list):
            temperature = single(temperature, "Mixture.temperature")
        if temperature is not None and not isinstance(temperature, dict):
            raise ConversionError("Mixture.temperature has no feed/outlet values")
        temperature = temperature or {}
        if "outlet" in temperature:
            put(sim, "has_simulated_reaction_temperature", temperature["outlet"])
        if "pressure" in mixture:
            put(sim, "has_simulated_reaction_pressure", mixture["pressure"])
        if "residence time" in mixture:
            put(sim, "has_simulated_reaction_residence_time", mixture["residence time"])
        if "hasDownstream" in data:
            flag = str(data["hasDownstream"]).strip()
            if flag not in ("Yes", "No"):
                raise ConversionError(f"hasDownstream has unexpected value {data['hasDownstream']!r}")
            sim["has_simulated_downstream"] = flag

        # --- feed (YAML: Mixture + Inlet) and product (YAML: Outlet + Outlet Composition) ---
        inlet = single(data["Inlet"], "Inlet") if "Inlet" in data else {}
        outlet = single(data["Outlet"], "Outlet") if "Outlet" in data else {}
        for key, section, allowed in (("Inlet", inlet, {"MolarFlow_In", "Comp_MolarFlow_In"}),
                                      ("Outlet", outlet, {"MolarFlow_Out", "Comp_MolarFlow_Out"})):
            if set(section) - allowed:
                raise ConversionError(f"unknown keys in '{key}': {sorted(set(section) - allowed)}")

        sim["has_initial_mixture"] = self.mixture(
            f"{sim_uri}_Feed",
            fractions=pairs(mixture.get("mole_fraction", []), "Mixture.mole_fraction"),
            flows=pairs(inlet.get("Comp_MolarFlow_In", []), "Comp_MolarFlow_In"),
            total_flow=inlet.get("MolarFlow_In"),
            temperature=temperature.get("feed"))
        if outlet or "Outlet Composition" in data:
            sim["has_product"] = self.mixture(
                f"{sim_uri}_Product",
                fractions=pairs(data.get("Outlet Composition", []), "Outlet Composition"),
                flows=pairs(outlet.get("Comp_MolarFlow_Out", []), "Comp_MolarFlow_Out"),
                total_flow=outlet.get("MolarFlow_Out"))
            if sim["has_product"].get("has_total_molar_flow") == 0:
                warnings.append("outlet molar flow is 0 (simulation probably not converged)")

        # --- downstream separator ---
        for key, slot, suffix in (("Sep_Gas Composition", "has_separator_gas_outlet", "SeparatorGas"),
                                  ("Sep_Liquid Composition", "has_separator_liquid_outlet", "SeparatorLiquid")):
            if key in data:
                sim[slot] = self.mixture(f"{sim_uri}_{suffix}", fractions=pairs(data[key], key), flows=[])

        # --- reactor ---
        if "Reactor" in data:
            reactor: dict[str, Any] = {"iri": f"{sim_uri}_Reactor"}
            for key, value in single(data["Reactor"], "Reactor").items():
                if key not in REACTOR_SLOTS:
                    raise ConversionError(f"unknown key in 'Reactor': {key}")
                put(reactor, REACTOR_SLOTS[key], value)
            sim["has_reactor"] = reactor

        # --- reaction mechanism: [[ {id, reactions: [ {equation, parameters} ]} ]] ---
        if "ChemicalReaction" in data:
            steps = []
            for mechanism in data["ChemicalReaction"]:
                for step in (mechanism if isinstance(mechanism, list) else [mechanism]):
                    if not isinstance(step, dict) or "reactions" not in step:
                        raise ConversionError(f"invalid entry in 'ChemicalReaction': {step!r}")
                    for n, params in enumerate(step["reactions"]):
                        suffix = f"{step.get('id', len(steps))}" + (f"_{n}" if len(step["reactions"]) > 1 else "")
                        reaction: dict[str, Any] = {"iri": f"{sim_uri}_Reaction_{suffix}"}
                        if "id" in step:
                            put(reaction, "has_reaction_id", step["id"])
                        for key, value in params.items():
                            if key not in REACTION_SLOTS:
                                raise ConversionError(f"unknown reaction parameter: {key}")
                            put(reaction, REACTION_SLOTS[key], value)
                        steps.append(reaction)
            sim["has_reaction_mechanism"] = {"iri": f"{sim_uri}_ReactionMechanism", "has_reaction_step": steps}

        # --- results ---
        for label, value in pairs(data.get("Turnover", []), "Turnover"):
            put(sim, f"has_turnover_{self.compound(label.removeprefix('X_'))[0]}", value)
        for label, value in pairs(data.get("Yield", []), "Yield"):
            put(sim, f"has_yield_{self.compound(label.removeprefix('Y_'))[0]}", value)
        for key, prefix in (("Selectivity_normed", "has_selectivity_co2_"),
                            ("Selectivity", "has_unnormalized_selectivity_co2_")):
            if key in data:
                for product, value in single(data[key], key).items():
                    put(sim, f"{prefix}{str(product).lower()}", value)

        # --- file references (format evaluated by Query.py) ---
        sim["comments"] = ([f"DWSIM-file: {dwsim_file}"] if dwsim_file else []) + [f"LinkML-file: {yaml_file}"]

        # --- plausibility (profiles are not converted, but indicate failed runs) ---
        coordinates = data.get("Coordinates") or []
        if len(coordinates) <= 1:
            warnings.append(f"axial profile has only {len(coordinates)} point(s)")
        return sim, warnings


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------
class Converter:
    def __init__(self, schema_path: Path, base_uri: str):
        log.info("Loading schema %s", schema_path)
        sv = self.schema_view = SchemaView(str(schema_path))
        self.target_cls = getattr(PythonGenerator(str(schema_path)).compile_module(), TARGET_CLASS)
        self.validator = Validator(str(schema_path), validation_plugins=[JsonschemaValidationPlugin(closed=True)])
        self.base_uri = base_uri if base_uri.endswith("/") else base_uri + "/"
        self.prefixes = {p.prefix_prefix: p.prefix_reference for p in sv.schema.prefixes.values()}

        compounds = {}
        for formula, pv in sv.get_enum(COMPOUND_ENUM).permissible_values.items():
            compounds[formula] = (snake(pv.description), sv.expand_curie(pv.meaning))
        self.builder = SimulationBuilder(compounds)

        # property IRI -> slot (for the declarations)
        self.slots_by_uri = {URIRef(sv.get_uri(s, expand=True)): s for s in sv.all_slots().values()}
        self.class_names = set(sv.all_classes())

    def declarations(self, graph: Graph) -> Graph:
        """owl:* declarations of all properties, classes and referenced individuals used in ``graph``."""
        sv = self.schema_view
        ranges = {"decimal": XSD.decimal, "integer": XSD.integer, "string": XSD.string}
        decl = Graph()
        todo = {p for p in graph.predicates() if p in self.slots_by_uri}
        done = set()
        while todo:
            uri = todo.pop()
            done.add(uri)
            slot = self.slots_by_uri[uri]
            if slot.slot_uri == "rdfs:comment":
                continue
            is_object = slot.range in self.class_names
            decl.add((uri, RDF.type, OWL.ObjectProperty if is_object else OWL.DatatypeProperty))
            if not (slot.annotations and "in_mv_onto" in slot.annotations):
                # properties defined by this schema get label, description and range
                decl.add((uri, RDFS.label, Literal(str(uri).split("#")[-1], lang="en")))
                if slot.description:
                    decl.add((uri, RDFS.comment, Literal(slot.description, lang="en")))
                if slot.range in ranges:
                    decl.add((uri, RDFS.range, ranges[slot.range]))
            if slot.is_a:
                parent = URIRef(sv.get_uri(sv.get_slot(slot.is_a), expand=True))
                decl.add((uri, RDFS.subPropertyOf, parent))
                if parent not in done:
                    todo.add(parent)
            if is_object:
                for _, _, target in graph.triples((None, uri, None)):
                    if (target, RDF.type, None) not in graph:  # referenced individual (substance)
                        decl.add((target, RDF.type, OWL.NamedIndividual))
        for cls in set(graph.objects(None, RDF.type)) - {OWL.NamedIndividual}:
            decl.add((cls, RDF.type, OWL.Class))
        return decl

    def to_turtle(self, yaml_path: Path, dwsim_name: str | None, collection: str) -> tuple[str, list[str], int]:
        with yaml_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)

        sim_uri = f"{self.base_uri}{collection}/{yaml_path.stem}"
        instance, warnings = self.builder.build(raw, sim_uri, dwsim_name, yaml_path.name)

        errors = [r.message for r in self.validator.validate(instance, TARGET_CLASS).results]
        if errors:
            raise ConversionError("schema validation failed: " + "; ".join(errors[:5]))

        graph = rdflib_dumper.as_rdf_graph(self.target_cls(**instance), schemaview=self.schema_view)
        individuals = set(graph.subjects(RDF.type, None))
        for individual in individuals:
            graph.add((individual, RDF.type, OWL.NamedIndividual))
        graph += self.declarations(graph)

        for prefix in ("afo", "reac4cat", "AFM", "AFE", "AFP", "exp"):
            graph.bind(prefix, self.prefixes[prefix], replace=True)
        graph.bind("owl", OWL)
        graph.bind("sim", f"{self.base_uri}{collection}/")
        turtle = graph.serialize(format="turtle")

        # check: the written Turtle must parse again and contain the same triples
        reparsed = Graph().parse(data=turtle, format="turtle")
        if len(reparsed) != len(graph):
            raise ConversionError(f"Turtle check failed ({len(reparsed)} != {len(graph)} triples)")
        return turtle, warnings, len(graph)


def process_folder(converter: Converter, input_dir: Path, output_root: Path, move: bool,
                   overwrite: bool, limit: int | None, report_rows: list[dict]) -> tuple[int, int, int]:
    collection = input_dir.name
    yaml_files = sorted(input_dir.glob("*.yaml"))
    if limit:
        yaml_files = yaml_files[:limit]
    log.info("%s: %d simulation YAML files", input_dir, len(yaml_files))

    ok = skipped = failed = 0
    start = time.perf_counter()
    for n, yaml_path in enumerate(yaml_files, 1):
        name = yaml_path.stem
        dwsim_path = yaml_path.with_suffix(".dwxmz")
        target_dir = output_root / collection / name
        ttl_path = target_dir / f"{name}.ttl"
        row = {"collection": collection, "simulation": name, "status": "", "triples": "", "message": ""}

        if ttl_path.exists() and not overwrite:
            skipped += 1
            row["status"] = "skipped (ttl exists)"
            report_rows.append(row)
            continue

        dwsim_name = dwsim_path.name if dwsim_path.exists() else None
        try:
            turtle, warnings, triples = converter.to_turtle(yaml_path, dwsim_name, collection)
        except Exception as exc:  # report and continue with the next file
            failed += 1
            log.error("%s: %s", name, exc)
            row.update(status="failed", message=str(exc))
            report_rows.append(row)
            continue

        if dwsim_name is None:
            warnings.append("no .dwxmz file found")
        for warning in warnings:
            log.debug("%s: %s", name, warning)

        target_dir.mkdir(parents=True, exist_ok=True)
        transfer = shutil.move if move else shutil.copy2
        for source in (yaml_path, dwsim_path):
            if source.exists():
                transfer(str(source), str(target_dir / source.name))
        ttl_path.write_text(turtle, encoding="utf-8")

        ok += 1
        row.update(status="ok (with warnings)" if warnings else "ok", triples=triples, message="; ".join(warnings))
        report_rows.append(row)

        if n % 50 == 0 or n == len(yaml_files):
            log.info("  %d/%d done (%.1f s)", n, len(yaml_files), time.perf_counter() - start)

    return ok, skipped, failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert DWSIM simulation YAMLs to Turtle using the LinkML schema.")
    parser.add_argument("inputs", nargs="+", type=Path, help="folder(s) with simulation .yaml/.dwxmz files, e.g. linkml/NewReaction_01")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help=f"LinkML schema (default: {DEFAULT_SCHEMA})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"output root (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--base-uri", default=DEFAULT_BASE_URI, help=f"base URI of the individuals (default: {DEFAULT_BASE_URI})")
    parser.add_argument("--move", action="store_true", help="move .dwxmz/.yaml into the simulation folders instead of copying them")
    parser.add_argument("--overwrite", action="store_true", help="convert again even if the .ttl already exists")
    parser.add_argument("--limit", type=int, help="only convert the first N files per folder (for testing)")
    parser.add_argument("-v", "--verbose", action="store_true", help="also print the plausibility warnings per file")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    logging.getLogger("linkml").setLevel(logging.WARNING)
    logging.getLogger("linkml_runtime").setLevel(logging.WARNING)
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    for input_dir in args.inputs:
        if not input_dir.is_dir():
            parser.error(f"not a folder: {input_dir}")

    converter = Converter(args.schema, args.base_uri)
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    report_rows: list[dict] = []
    totals = [0, 0, 0]
    for input_dir in args.inputs:
        result = process_folder(converter, input_dir.resolve(), output_root, args.move,
                                args.overwrite, args.limit, report_rows)
        totals = [a + b for a, b in zip(totals, result)]

    report_path = output_root / f"conversion_report_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["collection", "simulation", "status", "triples", "message"], delimiter=";")
        writer.writeheader()
        writer.writerows(report_rows)

    with_warnings = sum(1 for r in report_rows if r["status"] == "ok (with warnings)")
    log.info("Finished: %d converted (%d with warnings), %d skipped, %d failed", totals[0], with_warnings, totals[1], totals[2])
    log.info("Report: %s", report_path)
    return 1 if totals[2] else 0


if __name__ == "__main__":
    sys.exit(main())
