"""Upload NewReaction_01 simulation files to one NFDI4Cat Dataverse dataset."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import requests


BASE_URL = "https://repository.nfdi4cat.org"
DEFAULT_ROOT = Path(__file__).resolve().parent / "linkml" / "with_ttl" / "test" #"NewReaction_01"
DEFAULT_DESCRIPTION = (
    "Automated DWSIM simulation results for Ni-catalyzed methanation of carbon dioxide. "
    "Each simulation folder contains a DWSIM file and its TTL and YAML metadata sidecars."
)
FILE_SUFFIXES = (".dwxmz", ".ttl", ".yaml")


def collect_simulation_files(root):
    """Validate and return all three matching files from each immediate subfolder."""
    if not root.is_dir():
        raise FileNotFoundError(f"Simulation directory does not exist: {root}")

    simulation_folders = sorted(path for path in root.iterdir() if path.is_dir())
    if not simulation_folders:
        raise ValueError(f"No simulation folders found under {root}")

    prepared = []
    seen_names = set()
    for folder in simulation_folders:
        files_by_suffix = {
            suffix: [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() == suffix]
            for suffix in FILE_SUFFIXES
        }
        counts = {suffix: len(paths) for suffix, paths in files_by_suffix.items()}
        if any(count != 1 for count in counts.values()):
            raise ValueError(f"Expected one .dwxmz, .ttl, and .yaml file in {folder}: {counts}")

        files = tuple(files_by_suffix[suffix][0] for suffix in FILE_SUFFIXES)
        if len([path for path in folder.iterdir() if path.is_file()]) != len(files):
            raise ValueError(f"Unexpected additional files in {folder}")
        if len({path.stem for path in files}) != 1:
            raise ValueError(f"Expected matching file names in {folder}")

        for path in files:
            if path.name in seen_names:
                raise ValueError(f"Duplicate file name across simulation folders: {path.name}")
            seen_names.add(path.name)
        prepared.append((folder, files))

    return prepared


def dataset_metadata(title, description):
    def primitive(type_name, value):
        return {
            "typeName": type_name,
            "multiple": False,
            "typeClass": "primitive",
            "value": value,
        }

    def compound(type_name, records):
        return {
            "typeName": type_name,
            "multiple": True,
            "typeClass": "compound",
            "value": [
                {
                    name: primitive(name, value)
                    for name, value in record.items()
                }
                for record in records
            ],
        }

    citation_fields = [
        primitive("title", title),
        compound("author", [
            {"authorName": "Sommer-Behr, Alexander"},
            {"authorName": "Völkenrath, Marc"},
        ]),
        compound("datasetContact", [
            {
                "datasetContactName": "Sommer-Behr, Alexander",
                "datasetContactEmail": "alexander.behr@tu-dortmund.de",
            },
            {
                "datasetContactName": "Völkenrath, Marc",
                "datasetContactEmail": "marc.voelkenrath@tu-dortmund.de",
            },
        ]),
        compound("dsDescription", [{"dsDescriptionValue": description}]),
        {
            "typeName": "subject",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": ["Engineering", "Chemistry"],
        },
    ]
    return {
        "datasetVersion": {
            "metadataBlocks": {
                "citation": {
                    "displayName": "Citation Metadata",
                    "name": "citation",
                    "fields": citation_fields,
                }
            }
        }
    }


def file_metadata(path, folder_name):
    stem = path.stem
    suffix = path.suffix.lower()
    if suffix == ".dwxmz":
        description = f"DWSIM simulation data; metadata sidecars: {stem}.ttl and {stem}.yaml."
    elif suffix == ".ttl":
        description = f"TTL metadata describing the matching DWSIM file {stem}.dwxmz."
    elif suffix == ".yaml":
        description = f"YAML metadata describing the matching DWSIM file {stem}.dwxmz."
    else:
        raise ValueError(f"Unsupported file type: {path}")
    return {"description": description, "directoryLabel": folder_name}


def check_response(response, expected_status, operation):
    if response.status_code not in expected_status:
        raise RuntimeError(
            f"{operation} failed ({response.status_code}): {response.text}"
        )


def create_dataset(session, dataverse_alias, metadata):
    url = f"{BASE_URL}/api/dataverses/{quote(dataverse_alias, safe='')}/datasets"
    response = session.post(url, json=metadata, timeout=(30, 180))
    check_response(response, (201,), "Dataset creation")

    try:
        persistent_id = response.json()["data"]["persistentId"]
    except (ValueError, KeyError, TypeError) as error:
        raise RuntimeError("Dataset was created, but the API response had no persistent ID") from error
    return persistent_id


def upload_file(session, persistent_id, folder, path):
    url = f"{BASE_URL}/api/datasets/:persistentId/add"
    metadata = json.dumps(file_metadata(path, folder.name))
    with path.open("rb") as file_stream:
        response = session.post(
            url,
            params={"persistentId": persistent_id},
            files={"file": (path.name, file_stream)},
            data={"jsonData": metadata},
            timeout=(30, 180),
        )
    check_response(response, (200, 201), f"Upload of {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Methanation Simulation files directory")
    parser.add_argument(
        "--dataverse",
        default=os.environ.get("NFDI4CAT_DATAVERSE"),
        help="Target Dataverse alias (or set NFDI4CAT_DATAVERSE)",
    )
    parser.add_argument(
        "--title",
        default="Methanation simulation dataset - NewReaction_01",
        help="Title for the single dataset",
    )
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION)
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Create the dataset and upload files; without this flag only validate and preview",
    )
    args = parser.parse_args(argv)

    prepared = collect_simulation_files(args.root)
    total_files = sum(len(files) for _, files in prepared)
    print(f"Validated {len(prepared)} simulation folders ({total_files} files) under {args.root}.")
    print(f"Dataset title: {args.title}")
    print("File grouping: each simulation folder will be kept as a directory in the dataset.")
    if not args.upload:
        print("Preview only; pass --upload to create one dataset and upload the files.")
        return 0

    api_token = os.environ.get("NFDI4CAT_API_TOKEN")
    if not api_token:
        parser.error("Set the NFDI4CAT_API_TOKEN environment variable before uploading.")
    if not args.dataverse:
        parser.error("Provide --dataverse or set the NFDI4CAT_DATAVERSE environment variable.")

    session = requests.Session()
    session.headers.update({"X-Dataverse-key": api_token})
    persistent_id = create_dataset(
        session,
        args.dataverse,
        dataset_metadata(args.title, args.description),
    )
    print(f"Created dataset {persistent_id}; uploading {total_files} files.")

    uploaded = 0
    for folder, files in prepared:
        for path in files:
            upload_file(session, persistent_id, folder, path)
            uploaded += 1
            if uploaded % 25 == 0 or uploaded == total_files:
                print(f"Uploaded {uploaded}/{total_files} files.")

    print(f"Upload complete: {BASE_URL}/dataset.xhtml?persistentId={persistent_id}&version=DRAFT")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (requests.RequestException, RuntimeError, FileNotFoundError, ValueError) as error:
        sys.exit(f"Upload failed: {error}")
