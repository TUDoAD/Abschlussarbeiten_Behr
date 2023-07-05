# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 10:27:42 2023

@author: mvoel
"""

import os

# Der erste Pfad führt zur robot.jar und muss evtl. vom Nutzer angepasst werden.
# --input: ist die Ontologie in der nach den gewünschten IRI's gesucht werden soll.
# --method: kann nach Bedarf abgewandelt werden [http://robot.obolibrary.org/extract]
# --term-file: ist die Textdatei, in der die IRI's abgelegt sind welche gesucht werden sollen
# --output: selbsterklärend
bashCommand = "java -jar c://Windows/robot.jar extract --input Ontologien/pizza.owl --method BOT --term-file Ontologien/termfile.txt --output Ontologien/result.owl"

os.system(bashCommand)
