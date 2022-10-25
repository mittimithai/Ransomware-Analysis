from distutils import extension
import sys
import os
import time
from sys import exit
from attr import has
from tqdm import tqdm

vmName = "ransomware"
username = "ransomware"
password = "helloworld"
snapshotName = "defenderDisabled"
procmonPath = f"C:\\Users\\{username}\\Downloads\\ProcessMonitor\\Procmon.exe"
downloadPath = f"C:\\Users\\{username}\\Downloads"
cmdPath = "C:\Windows\System32\cmd.exe"
BazaarApiKey = "82ea76c5b51d6e9ea0b08dba6a18771e"
secondaryStoragePath = "E:\Ransomware 2023\logsDump.vdi"
extractionPath = "E:\\"
vmStartTime = 200
ransomwareExecTime = 900
vmClosingTime = 5
ransomwareExtension = "exe"
hashFilePath = f"E:\Ransomware 2023"
hashFileName = f"hashes_exe.txt"
runs = 5

def vboxManage(programPath, programArg, cmdType):
    count = 0

    while(1):
        output = os.system(f'''VBoxManage guestcontrol "{vmName}" {cmdType} --exe {programPath} --username "{username}" --password {password} -- {programPath} {programArg} ''')

        # after 3 tries of executing the command, execption will be raised
        if count == 4:
            raise Exception("Unable to execute the command")

        # reexecute the command because the vm is not ready
        elif output == 1:
            time.sleep(60)
            count = count + 1
            continue

        # unable to download the hash becuase it is invalid, raise exception
        elif output == 33:
            print("hash invalid")
            deleteHash(hashFilePath, ransomwareExtension)
            raise Exception("Unable to execute the command")

        # for any other type of error, raise exception
        elif output !=0:
           raise Exception("Unable to execute the command")
        else:
            return

def extrachHash(hashFilePath, hashFileName, ransomwareExtension):

    # check if there is any hash left in the file, otherwise close
    filesize = os.path.getsize(f"{hashFilePath}\\{hashFileName}")
    if filesize == 0:
        sys.exit("file is empty")

    # read the hash from the file
    try:
        with open(f"{hashFilePath}\\{hashFileName}", 'r') as f:
            hash = f.readline()
            return hash.strip()

    except:
        print("Error: Unable to read the file")

def deleteHash(hashFilePath, hashFileName, ransomwareExtension):

    # check if there is any hash left in the file, otherwise close
    filesize = os.path.getsize(f"{hashFilePath}\\{hashFileName}")
    if filesize == 0:
        sys.exit("file is empty")

    # delete the first line(hash) from the file
    try:
        with open(f"{hashFilePath}\\{hashFileName}", 'r') as fr:
            # reading line by line
            lines = fr.readlines()

            # pointer for position
            ptr = 1
            # opening in writing mode
            with open(f"{hashFilePath}\\{hashFileName}", 'w') as fw:
                for line in lines:

                    # we want to remove 5th line
                    if ptr != 1:
                        fw.write(line)
                    ptr += 1
    except:
        print("Error:Unable to delete the hash")

def saveHash(hashFilePath, ransomwareExtension, hash_value):

    # save the hash to a new file
    try:
        with open(f"{hashFilePath}\\hashes_done_{ransomwareExtension}.txt", 'a') as fw:
            fw.write(hash_value+'\n')
    except:
        print("Error:Unable to delete the hash")

# counter to track number of iterations
count = 0
while(count != runs):
    try:
        # starts the vm and sets up username and password
        os.system(f"VBoxManage startvm {vmName}")
        os.system(f'VBoxManage controlvm {vmName} setcredentials {username} {password} "DOMTEST"')

        # reads hash from the file and print it
        print("extracting hash")
        hash_value = extrachHash(hashFilePath, hashFileName, ransomwareExtension)
        print("Hash:", hash_value)

        # downloads ransomware from bazaar api
        print("downloading ransomware")
        vboxManage(cmdPath, f'''/c "bazaar init {BazaarApiKey}" ''', "run")
        vboxManage(cmdPath, f'''/c "bazaar download {hash_value} --unzip --output {downloadPath}\\{hash_value}.{ransomwareExtension}" ''', "run")

        # opens procmon and start logging in a backing file
        print("ransomware downloaded, opening procmon")
        vboxManage(procmonPath, f'''/AcceptEula /Nofilter /Quiet /BackingFile "{downloadPath}\\{hash_value}.PML" /Runtime {ransomwareExecTime}''', "start")
        vboxManage(procmonPath, f'''/waitforidle ''', "run")

        # triggers ransomware
        print("procmon started, triggering ransomware")
        vboxManage(cmdPath, f'''/c "{downloadPath}\\{hash_value}.{ransomwareExtension}" ''', "start")

        # waiting for the ransomware to attack
        print("ransomware triggered, waiting for attack")
        for i in tqdm(range(ransomwareExecTime+40)):
            time.sleep(1)

        # closing the vm
        print("Procmon closed, closing vm")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)

        # mounting the secondary drive to move procmon logs to
        print("vm closed, mounting secondary drive")
        os.system(f'''VBoxManage storageattach {vmName} --storagectl SATA --port 2 --type hdd --medium "{secondaryStoragePath}" ''')

        # restarting the vm and setting up the username and password and waiting for it to start
        print("drive mounted, starting vm")
        os.system(f"VBoxManage startvm {vmName}")
        os.system(f'VBoxManage controlvm {vmName} setcredentials {username} {password} "DOMTEST"')
        for i in tqdm(range(vmStartTime)):
            time.sleep(1)

        # waiting for the logs to move and procmon to close properly
        print("vm started, starting extraction")
        vboxManage(procmonPath, f'''/AcceptEula /OpenLog {downloadPath}\\{hash_value}.PML /SaveAs {extractionPath}\\{hash_value}.PML''', "run")
        for i in tqdm(range(40)):
            time.sleep(1)

        # closing vm
        print("extraction done, closing vm")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)

        # unmounting the secondary drive
        print("vm closed, unmounting secondary drive")
        os.system(f"VBoxManage storageattach {vmName} --storagectl SATA --port 2 --medium none")

        # restoring the vm back to a fresh snapshot
        print("secondary drive unmounted, restoring snapshot")
        os.system(f'''VBoxManage snapshot {vmName} restore {snapshotName}''')
        print("snapshot restored")

        # saving the hash as done and deleting it from the original file
        saveHash(hashFilePath, ransomwareExtension, hash_value)
        deleteHash(hashFilePath, hashFileName, ransomwareExtension)
        count = count + 1

    # if hashfile is empty, close vm and restore snapshot
    except SystemExit:
        print("file is empty")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)
        print("Restoring Snapshot")
        os.system(f'''VBoxManage snapshot {vmName} restore {snapshotName}''')
        print("snapshot restored")
        break

    # if keyboard interrupt, close vm and restore snapshot
    except KeyboardInterrupt:
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)
        print("Restoring Snapshot")
        os.system(f'''VBoxManage snapshot {vmName} restore {snapshotName}''')
        print("snapshot restored")
        break

    # if any other exception occured, close vm and resotre snapshot and restart the iteration
    except:
        print("Error: Exception occured, closing vm")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)
        print("Restoring Snapshot")
        os.system(f'''VBoxManage snapshot {vmName} restore {snapshotName}''')
        print("snapshot restored")
        continue

# /SaveApplyFilter
# 100, 100,80
# 200, 100,80
# 300, 100,80
# 400, 100,80
# 500, 100,80
# 600, 100,80
# 700, 100,80
# 800, 100,80
# 900, 100,80
# 1000, 100,80
# 1500, 100,80
# 1800, 100,40
# 1800, 60,40
# 1800, 40,40


hash_value = "3137413d086b188cd25ad5c6906fbb396554f36b4444441d5cff5a2176c28dd29fb0a"
# ans = os.system(f'''VBoxManage guestcontrol "{vmName}" run --exe {cmdPath} --username "{username}" --password {password} -- {cmdPath} /c "bazaar init {BazaarApiKey}" ''')
# ans = os.system(f"VBoxManage startvm {vmName}")
# # # ans = os.system(f'''VBoxManage guestcontrol "{vmName}" run --exe {cmdPath} --username "{username}" --password {password} -- {cmdPath} /c "bazaar download {hash_value} --unzip --output {downloadPath}\\{hash_value}.exe" ''')
# print(ans)
#vboxManage(procmonPath, f'''/AcceptEula /Nofilter /Quiet /BackingFile "{downloadPath}\\{hash_value}.PML" /Runtime {ransomwareExecTime}''', "start")
