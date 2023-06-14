# Reproduktion des Codes
Bevor der der Code **00_2023_MA_Abbaspour_Pythoncode.py abgespielt** werden kann, müssen folgende Vorbereitungen getroffen werden:
### (1) Import der neuen chemischen Substanzen in die DWSIM-Stoffdatenbank:
- Chemische Substanzen, die nicht in einer der Stoffdatenbanken vorliegen, die DWSIM unterstützt, können manuell in die DWSIM-Stoffdatenbank importiert werden
- Dafür wird der Code **CreateCompound_inDWSIM_JSON.py** aus dem GitHub-Unterordner *substances* ausgeführt
- Mit diesem Code wird eine Pseudoverbindung für jeden Eintrag in der Liste aus Zeile 70 erstellt und als JSON-Datei in dem DWSIM-Unterordner *addcomps* abgespeichert
- Im Code werden die relativen Dichten und die Normalsiedetemperaturen der zu erstellenden chemischen Substanzen angegeben (siehe Z. 71 und 72)
- Anschließend werden drei Abschätzungsmethoden, die in DWSIM integriert sind, abgerufen, um fehlende Substanzeigenschaften von DWSIM abschätzen zu lassen (siehe Zeile 78 bis 83) 
- Dann müssen Anfangswerte für das Molekulargewicht (mw0), die spezifische Gravität (sg0) und den Normalsiedepunkt (nbp0) angegeben werden ( siehe Z. 87 bis 89)
- Nach Abspielen des Codes sind die Dateien *Laccase.json, ABTS_red.json und ABTS_ox.json* im genannten Ordner zu finden
- Die drei JSON-Dateien werden geöffnet: Da die Werte für die Stoffeigenschaften stark von den eigentlichen Werten abweichen (vgl. z. B. das Molekulargewicht von Laccase), werden **händisch** die richtigen Werte eingetragen
- Für fehlende Substanzeigenschaften, wie kritische Parameter (z. B. Tc, Pc) werden Werte des **Lösemittels Wasser** angenommen (hierfür wird der Stoff Wasser als JSON-Datei aus der DWSIM-Software exportiert werden und die Einträge werden manuell in die Dateien Laccase.json, ABTS_red.json und ABTS_ox.json abgeschrieben. **Aber**, nicht alles auf einmal Copy-Pasten, sondern Einträge einzeln ändern)
- Die so erzeugten JSON-Dateien sind im GitHub unter dem Unterordner *substances* abgelegt

### (2) Alle Dateien, auf die der **Code 00_2023_MA_Abbaspour_Pythoncode.py** zugreift müssen zusammen im selben Ordner wie der Code abgelegt sein:
- Die zusammengeführte Ontologie **BaseOnto.owl**, die im GitHub-Unterordner *ontologies* abgelegt ist
- Das EnzymeML-Excel-ELN **EnzymeML_Template_18-8-2021_KR.xlsm** und das ergänzende ELN **Ergänzendes Laborbuch_Kinetik_1.xlsx** oder **Ergänzendes Laborbuch_Kinetik_1.xlsx**, die im GitHub-Unterordner *ELNs* abgespeichert sind

![Workflow_Pythoncode](https://github.com/TUDoAD/Abschlussarbeiten_Behr/assets/117766304/a44f3dfd-f1a4-46ea-8a86-9e4070a97a5b)
