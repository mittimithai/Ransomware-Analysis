# # import OS module
import os
import time
import threading
import sys

#host configuration
hostName = "phdlab"
procmonPath = f"C:\\Users\\{hostName}\\Downloads\\ProcessMonitor\\Procmon64"
ProcmonfilterFilePath = f"C:\\Users\\{hostName}\\Downloads\\ProcessMonitor\\spade.reporter.ProcMon.pmc"
pmlPath = "E:\\extraction\\logs"
xmlTempPath = "E:\\extraction\\xmlTemp\\"
pmlDonePath = "E:\\extraction\\pmlDone\\"
xmlPath = "E:\\extraction\\xmls\\"

#vm configuration
getopsFilePath = "/home/spades/Desktop/getops.py"
spadeVmUsername = "spades"
spadeVmPassword = "helloworld"
spadeVmName = "spade"

def convert(ransomware):
    os.system(f'''{procmonPath} /OpenLog {pmlPath}\\{ransomware}.PML /LoadConfig {ProcmonfilterFilePath} /SaveAs {xmlTempPath}\\{ransomware}.XML''' )
    os.system(f'''move {pmlPath}\\{ransomware}.PML {pmlDonePath}\\{ransomware}.PML''')
    os.system(f'''move {xmlTempPath}\\{ransomware}.XML {xmlPath}\\{ransomware}.XML''' )

dir_list = os.listdir(pmlPath)
while(1):
	dir_list = os.listdir(pmlPath)
	if dir_list:
		file = dir_list[0]
		ransomware = file.split('.')[0]
		print(ransomware)
		t1 = threading.Thread(target=convert, args=(ransomware,))
		t1.start()
	else:
		print("No logs available")
		
	time.sleep(1800)	
		

#os.system(f'''VboxManage guestcontrol "{spadeVmName}" run --exe {getopsFilePath} --username "{spadeVmUsername}" --password "{spadeVmPassword}"''')

# # Get the list of all files and directories
# path = "E:\\vm3\\PMLs"
# dir_list = os.listdir(path)
# procmonPath = "C:\\Users\\phdlab\\Downloads\\ProcessMonitor\\Procmon64"
# configPath = "C:\\Users\\phdlab\\Downloads\\ProcessMonitor\\spade.reporter.ProcMon.pmc"
# counter = 0

# #os.system(f'''{procmonPath} /OpenLog E:\\vm3\\PMLs\\{ransomware}.PML /LoadConfig {configPath} /SaveAs E:\\vm3\\XMLshared\\xmls\\{ransomware}.XML''' )
# #os.system(f'''VboxManage guestcontrol "spade" run --exe /home/spades/Desktop/getops.py --username "spades" --password "helloworld"''')
# #os.system(f'''VboxManage guestcontrol "spade" run --exe /home/spades/SPADE/bin/manage-postgres.sh --username "spades" --password "helloworld" -- /home/spades/SPADE/bin/manage-postgres.sh clear''')
# #os.system(f'''VboxManage guestcontrol "spade" run --exe /usr/bin/xterm --username "spades" --password "helloworld" -- /usr/bin/xterm "/home/spades/SPADE/bin/manage-postgres.sh''')

# def convert(ransomware):
#     os.system(f'''{procmonPath} /OpenLog E:\\vm3\\PMLs\\{ransomware}.PML /LoadConfig {configPath} /SaveAs E:\\vm3\\XMLtemp\\{ransomware}.XML''' )
#     os.system(f'''move E:\\vm3\\PMLs\\{ransomware}.PML E:\\vm3\\PMLsdone''')
#     os.system(f'''move E:\\vm3\\XMLtemp\\{ransomware}.XML E:\\vm3\\XMLshared\\xmls\\{ransomware}.XML''' )
#     #os.system(f'''del "E:\\vm3\\PMLs\\{ransomware}.PML''' )

# for file in dir_list:
#     if "txt" in file:
#         continue
#     if counter == 50:
#         break
#     ransomware = file.split('.')[0]
#     print(ransomware)
#     t1 = threading.Thread(target=convert, args=(ransomware,))
#     t1.start()
#     time.sleep(600)
#     counter = counter + 1