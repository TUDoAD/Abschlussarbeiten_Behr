# Todo:
	- Alignment zu BFO, SBO, AFO, reac4cat !	
		in SBO enthalten:
			- kcat = Turnover number / Catalytic rate constant -> in SBO:0000025 modelliert
			- km = Michaelis constant -> in SBO:0000027 modelliert
			- Reaction type -> näher klassifizieren
				- Michaelis Menten Kinetic = Henri-Michaelis-Menten rate law (SBO:0000029) 
					- kcat = SBO:0000025 -> catalytic Rate Constant
					-	Et = SBO:0000505 -> Concentration of Enzyme
					-	 S = SBO:0000515 -> Concentration of Substrate
					-   Ks = SBO:0000373 -> Michaelis Constant in Fast Equilibrium situation
					
	- Gedanken zu integration in DEXPI machen
	- Erste Ideen für Paper mit Katrin aufschreiben!
	- measurement .addData ausprobieren bei pyenzyme Dokument
	- Vergleiche eigenes ELN/DataProperties mit denen von EnzymeML 
		- Eliminiere Doppelungen!		
	- Reaktorklassifikation über STRENDA ?
	https://github.com/StephanM87/Strenda-biocatalysis/tree/main


## Coding

### Ontologien
- Testaufbau der finalen Ontologie in **Finale_Onto_mod.owl**
	- WIP Ontologie hier: **Substances_and_BaseOnto2.owl**
- Entsprechendes Anpassen der **BaseOnto.owl** -> Importiert jetzt SBO komplett!
- Code restrukturieren und auf BaseOnto anpassen
- Allgemein auf s0, s1, s2 usw. achten, dass richtig aufgeschrieben in den ELNs !
- Handschriftl. Notizen !
- Reasoning prüfen


- General Class Axioms in Python -> Links von Hendrik anschauen!
- Reac4Cat Prinzip einbauen

### Reaction + Substances
Catalyst: [Laccase] -> Laccase Substance: http://purl.obolibrary.org/obo/GO_1990204 Laccase activity: http://purl.obolibrary.org/obo/GO_0016682

Oxidoreductase activity(is_a http://purl.obolibrary.org/obo/GO_0016491):

Laccase activity (is_a http://purl.obolibrary.org/obo/GO_0016682):
		{Educts:[ABTS_red is_a https://www.wikidata.org/wiki/Q287582], O2],
	     Products:[H2O, ABTS_ox],
	     Catalyst:[Laccase is_a http://purl.obolibrary.org/obo/GO_1990204]},
		 
		 
 
## Kompetenzfragen
Zu welcher Art der Reaktionen gehörte die Reaktion im EnzymeML-Dokument? 
BZW.: Welche Art der Reaktion wurde katalysiert?
Mit welcher Art Kinetik wurde die Reaktion modelliert? 

