import os
import threading
import time
import signal
#vm configuration
vmName = "ransomwareVm"
username = "ransomware"
password = "helloworld"
snapshotName = "Snapshot1"
cmdPath = "C:\Windows\System32\cmd.exe"
procmonPath = f"C:\\Users\\{username}\\Downloads\\ProcessMonitor\\Procmon.exe"
ProcmonfilterFilePath = f"C:\\Users\\{username}\\Downloads\\ProcessMonitor\\spade.reporter.ProcMon.pmc"
ransomwareDownloadPath = f"C:\\Users\\{username}\\Downloads"
BazaarApiKey = "82ea76c5b51d6e9ea0b08dba6a18771e"
logSavingPathVm = "E:\\"
densityscoutPath = "E:\\densityscout_build_45_windows\\win64\\densityscout.exe"
densitySavingPath = "E:\\"
folderForDensity = f"C:\\Users\\{username}\\Desktop"
vmStartTime = 70
vmClosingTime = 5
logsDumpVdiPathVm = "F:\\"

#host configuration
current_directory = os.getcwd()
secondaryVdiPath = f"{current_directory}\\vm_logsDump.vdi"
extractionPathHost = f"{current_directory}"
ransomwareExecTime = 600
ransomwareExtension = "exe"
hashFilePath = f"{current_directory}"
hashFileName = f"vm_hashes_exe.txt"
runs = 200
sreenshotsPath = f"{hashFilePath}\\screenshots"
zipPath = f"{current_directory}\\7-Zip\\7z.exe"
hostName = "phdlab"
procmonPathHost = f"{current_directory}\\ProcessMonitor\\Procmon64"
ProcmonfilterFilePathHost = f"{current_directory}\\ProcessMonitor\\spade.reporter.ProcMon.pmc"
pmlPath = f"{current_directory}\\logs"
pmlDonePath = f"{current_directory}\\pmlDone\\"
xmlPath = f"{current_directory}\\xmls\\"
density_path = f"{current_directory}\\density"
file_ops_path = f"{current_directory}\\file_ops"
csv_file_path = f"{current_directory}\\summary.csv"
sampleDensityPath = f"{current_directory}\\sampleDensity.txt"
csvPopulatePath = f"{current_directory}\\csv_populate.py"
vmAutomationPath = f"{current_directory}\\vmAutomation.py"
extractXmlPath = f"{current_directory}\\extractXML.py"
procmonTimeout = 1200

#spadeVm Configuration
spadeVmName = "spadeVm"
spadeVmUsername = "spades"
spadeVmPass = "helloworld"
spadeVmStartTime = 30
spadeVmSnapshot = "Snapshot1"
spadeVmCloseTime = 5
getOpsPaths = "/media/sf_extraction/getops.py"
getFileOperationsPath = "/media/sf_extraction/getFileOperations.py"
sharedFolderPath = f"{current_directory}"