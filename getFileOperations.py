#!/usr/bin/python3

import sys
import os
import time


directory = "/media/sf_extraction"
xmlPath = "/media/sf_extraction/xmls"
scriptPath = "/media/sf_extraction/get_fileops.sh"
xmlsDone = []
os.system("sudo /home/spades/SPADE/bin/spade start")

dir_list = os.listdir(xmlPath)

file = dir_list[0]

ransomware = file.split('.')[0]

os.system(f''' echo {xmlPath}/{file}''')

os.system(f'''sudo {scriptPath} {directory} {ransomware}''')

os.system("sudo /home/spades/SPADE/bin/spade stop")

time.sleep(10)
