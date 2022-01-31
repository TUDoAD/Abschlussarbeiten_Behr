Bevor der Code angewendet werden kann, müssen folgende Ordner dort erstellt werden, wo auch die .py Dateien abgelegt sind.
Ordner: import, json-files, models, pickle

Die zu analysierenden PDF-Dateien werden im Ordner "import" abgelegt.

Nachfolgend eine allgemeine Beschreibung welche Skripte durchlaufen werden.
Welche Schritte dazu im jeweiligen Python-Skript ablaufen, ist an entsprechender Stelle im jeweiligen Skript kommentiert. 


===============================================================================================================================================================================
Das Programm wird über das Skript "run.py" gestartet, welches alle anderen benötigten Skripte/ Funktionen aufruft. 
Diesem Skript muss eine Name und ein Wert für den Min_Count Parameter von Word2Vec übergeben werden.

	run.textmining(name, mincount)


Zunächst wird pdf_globing.py aufgerufen, welches dazu dient den Text aus den PDF-Dateien zu extrahieren. 
Der eingelesene Text (String) wird anschließend in einer pickle-Datei im entsprechenden Ordner gespeichert.

Anschließend erfolgt das Preprocessing des Textes anhand des Skriptes "data_preprocessing_spacy.py". 
Der vorbereitete Text (nun vorliegen als Listen mit den zu analysieren Token) wird ebenfalls als pickle-Datei im entsprechenden Ordner gespeichert.

Anhand des Skriptes "w2v_training.py" wird ein Word2Vec Modell erstellt, welches anschließend im Ordner "models" gespeichert wird.

Dieses Modell wird durch das Skript "clustering.py" einer Clusteranalyse unterzogen. Für das erstellte Dendrogramm wird dabei eine Baumstruktur erstellt und in einer JSON-Datei
im entsprechenden Ordner gespeichert. 

Im Skript "jparsing" werden die Wortpaare anhand des Pfades der JSON-Datei bestimmt und dessen Oberbegriffe extrahiert. Für die neu entstandenen Wortpaare wird dieser Prozess
rekursiv durchlaufen, bis alle Oberbegriffe gefunden wurden oder das Programm 1000 (anpassbar) Rekursionen überschreitet.

Anschließend wird durch das Skript "result_lists.py" die Anzahl gefundener Oberbegriffe bestimmt.

Abschließend werden durch das Skript "xlsx_postprocessing.py" die Duplikate gelöscht. Weiterhin werden hier Strings geändert in denen Klassen, bestehend aus mehreren Worten, 
welche durch "_" getrennt sind vorkommen. Das "_" wird dabei durch ein Leerzeichen ersetzt.
Die erstellte Klassenliste wird dann in einer Excel-Datei gespeichert. 
===============================================================================================================================================================================

