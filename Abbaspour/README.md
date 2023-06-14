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

# Workflow

![Workflow_Pythoncode](https://github.com/TUDoAD/Abschlussarbeiten_Behr/assets/117766304/a44f3dfd-f1a4-46ea-8a86-9e4070a97a5b)

(1) Zunächst wird das Python-Modul *PyEnzyme* importiert und die gewünschte Datei **EnzymeML_Template_18-8-2021_KR.xlsm** über die Methode *fromTemplate* in die Python-Umgebung geladen. Anschließend wird über vier *for-Schleifen* durch das Dokument iteriert und Informationen zum Benutzer, zum Behälter, zur Reaktion und zum Protein in entsprechende Variablen gespeichert.\n
(2) Danach werden die Dateien **BaseOnto.owl** und **Ergänzendes Laborbuch_Kinetik_1.xlsx** aufgerufen.
(3) Es folgt die Entwicklung der Ontologie, wobei über die Funktionen *class_creaction* und *dataProp_creation* erst Substanzklassen und dann Stoffeigenschaften als Data Properties erstellt werden. Die Data Properties werden über die Funktion *set_relation* den Substanzklassen zugewiesen.
(4) Die Ontologie wird zwischengespeichert als **Zwischenstand_Onto_.owl** (siehe GitHub-Unterordner *ontologies*) und wieder aufgerufen.
(5) Erweiterung von **Zwischenstand_Onto_.owl** mit Entitäten, denen alle Daten aus den ELNs zugeordnet werden, und Abspeichern der final verwendeten Ontologie als **Finale_Onto_.owl** (siehe GitHub-Unterordner *ontologies*).
(6) Anschließend folgt die Modellierung des Laborversuches in DWSIM. Dafür werden die DWSIM-Pakete importiert und die Reaktionsteilnehmer in die Python-Umgebung geladen.
(7) Den Reaktionsteilnehmern werden die entsprechenden stöchiometrischen Koeffizienten sowie die Reaktionsordnungekoeffizientne für die Vor- und Rückwärtsreaktion zugeordnet. Die jeweiligen Werte werden aus der Ontologie aufgerufen und an DWSIM übergeben. 
(8) Mit der Methode *CreateKinetikReaction* in Zeile 805 wird die Arrhenius-Kinetik in DWSIM importiert. Das ist wichtig, um später das eigene Sktipt des Script Managers abspielen lassen zu können. Denn der Name, der hier als Argument übergeben wird (in diesem Fall ist es die Variable Reaction_Name, die den Namen ABTS-Oxidation speichert) muss mit dem Argument in Zeile 961 übereinstimmen.
(9) Nachdem das Prozessfließbild erstellt wird, werden die eingehenden Materialströme definiert, wobei die Stoffmengenströme und Volumentröme aus der Ontologie ausgelesen und DWSIM übergeben werden.
(10) Anschließend wird das externe Skript für den Script Manager erstellt und ausgeführt.
(11) Abschließend werden die Berechnung und die Ausgabe des PFDs als PNG angefordert.
(12) Die Ausführung des Pythoncodes sollte nicht länger als 40-45 Sekunden dauern. Am Ende wird ein PNG mit dem PFD ausgegeben und auf dem Desktop wird die Simulations-Datei ABTS_Oxidation.dwxmz erstellt. 
