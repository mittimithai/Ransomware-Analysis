import sys
import os
import time
from sys import exit
from tqdm import tqdm

#vm configuration
vmName = "ransomware2"
username = "ransomware"
password = "helloworld"
snapshotName = "Snapshot1"
procmonPath = f"C:\\Users\\{username}\\Downloads\\ProcessMonitor\\Procmon.exe"
ransomwareDownloadPath = f"C:\\Users\\{username}\\Downloads"
cmdPath = "C:\Windows\System32\cmd.exe"
BazaarApiKey = "82ea76c5b51d6e9ea0b08dba6a18771e"
logSavingPathVm = "E:\\"
ProcmonfilterFilePath = f"C:\\Users\\{username}\\Downloads\\ProcessMonitor\\spade.reporter.ProcMon.pmc"
densityscoutPath = "E:\\densityscout_build_45_windows\\win64\\densityscout.exe"
densitySavingPath = "E:\\"
folderForDensity = f"C:\\Users\\{username}\\Desktop"
logsDumpPathHost = "F:\\"

#host configuration
secondaryVdiPath = "D:\\vm1\\vm1_logsDump.vdi"
extractionPathHost = "E:\\extraction"
vmStartTime = 70
ransomwareExecTime = 600
vmClosingTime = 5
ransomwareExtension = "exe"
hashFilePath = f"D:\\vm1"
hashFileName = f"vm1_hashes_exe.txt"
runs = 200
sreenshotsPath = f"{hashFilePath}\\screenshots"
zipPath = "C:\\Program Files\\7-Zip\\7z.exe"



def vboxManage(programPath, programArg, cmdType):
    count = 0

    while(1):
        output = os.system(f'''VBoxManage guestcontrol "{vmName}" {cmdType} --exe {programPath} --username "{username}" --password {password} -- {programPath} {programArg} ''')

        # after 3 tries of executing the command, execption will be raised
        if count == 3:
            raise Exception("Unable to execute the command")

        # reexecute the command because the vm is not ready
        elif output == 1:
            time.sleep(60)
            count = count + 1
            continue

        # unable to download the hash becuase it is invalid, raise exception
        elif output == 33:
            count = count + 1
            continue

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
        with open(f"{hashFilePath}\\vm1_hashes_done_{ransomwareExtension}.txt", 'a') as fw:
            fw.write(hash_value+'\n')
    except:
        print("Error:Unable to save the hash")

def retryHash(hashFilePath, ransomwareExtension, hash_value):

    # save the hash to a new file
    try:
        with open(f"{hashFilePath}\\vm1_hashes_retry_{ransomwareExtension}.txt", 'a') as fw:
            fw.write(hash_value+'\n')
    except:
        print("Error:Unable to save retry hash")

# counter to track number of iterations
count = 0
while(count != runs):
    try:
        # starts the vm and sets up username and password
        os.system(f"VBoxManage startvm {vmName}")
        os.system(f'VBoxManage controlvm {vmName} setcredentials {username} {password} "DOMTEST"')
        for i in tqdm(range(vmStartTime)):
            time.sleep(1)

        # reads hash from the file and print it
        print("extracting hash")
        hash_value = extrachHash(hashFilePath, hashFileName, ransomwareExtension)
        print("Hash:", hash_value)

        #calculating density prior
        print("calculating density")
        vboxManage(cmdPath, f'''/c "{densityscoutPath} -d -r -o {densitySavingPath}\\densityBefore.txt {folderForDensity}" ''', "run")

        # downloads ransomware from bazaar api
        print("downloading ransomware")
        vboxManage(cmdPath, f'''/c "bazaar init {BazaarApiKey}" ''', "run")
        vboxManage(cmdPath, f'''/c "bazaar download {hash_value} --unzip --output {ransomwareDownloadPath}\\{hash_value}.{ransomwareExtension}" ''', "run")

        #opens procmon and start logging in a backing file
        print("ransomware downloaded, opening procmon")
        vboxManage(procmonPath, f'''/BackingFile {logSavingPathVm}\\{hash_value}.pml /NoFilter /AcceptEula /LoadConfig {ProcmonfilterFilePath} /Quiet''', "start")
        vboxManage(procmonPath, f'''/waitforidle ''', "run")

        # triggers ransomware
        print("procmon started, triggering ransomware")
        vboxManage(cmdPath, f'''/c "{ransomwareDownloadPath}\\{hash_value}.{ransomwareExtension}" ''', "start")

        # waiting for the ransomware to attack
        print("ransomware triggered, waiting for attack")
        for i in tqdm(range(ransomwareExecTime)):
            time.sleep(1)

        #taking screenshot of the desktop
        os.system(f"VBoxManage controlvm {vmName} screenshotpng {sreenshotsPath}\\{hash_value}.png")

        #calculating density after
        print("calculating density")
        vboxManage(cmdPath, f'''/c "{densityscoutPath} -d -r -o {densitySavingPath}\\densityAfter.txt {folderForDensity}" ''', "run")

        #closing procmon
        vboxManage(procmonPath, f'''/Terminate''', "start")
        time.sleep(180)

        # closing the vm
        print("Procmon closed, closing vm")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)

        # mounting the secondary drive to move procmon logs to
        print("vm closed, mounting secondary drive")
        os.system(f'''VBoxManage storageattach {vmName} --storagectl SATA --port 3 --type hdd --medium "{secondaryVdiPath}" ''')

        # restarting the vm and setting up the username and password and waiting for it to start
        print("drive mounted, starting vm")
        os.system(f"VBoxManage startvm {vmName}")
        os.system(f'VBoxManage controlvm {vmName} setcredentials {username} {password} "DOMTEST"')
        for i in tqdm(range(vmStartTime)):
            time.sleep(1)

        # waiting for the logs to move and procmon to close properly
        print("vm started, starting extraction")
        vboxManage(cmdPath, f'''/c del F:\\*.pml''', "run")
        vboxManage(cmdPath, f'''/c del F:\\*.txt''', "run")

        vboxManage(cmdPath, f'''/c move {densitySavingPath}\\densityAfter.txt {logsDumpPathHost}\\{hash_value}_after.txt''', "run")
        vboxManage(cmdPath, f'''/c move {densitySavingPath}\\densityBefore.txt {logsDumpPathHost}\\{hash_value}_before.txt''', "run")
        vboxManage(cmdPath, f'''/c move {logSavingPathVm}\\{hash_value}.pml {logsDumpPathHost}\\{hash_value}.pml''', "run")
        time.sleep(80)

        # closing vm
        print("extraction done, closing vm")
        os.system(f"VBoxManage controlvm {vmName} poweroff")
        time.sleep(vmClosingTime)

        # unmounting the secondary drive
        print("vm closed, unmounting secondary drive")
        os.system(f"VBoxManage storageattach {vmName} --storagectl SATA --port 3 --medium none")

        # restoring the vm back to a fresh snapshot
        print("secondary drive unmounted, restoring snapshot")
        os.system(f'''VBoxManage snapshot {vmName} restore {snapshotName}''')
        print("snapshot restored")

        # extracting the logs and density file
        os.system(f'''"{zipPath}" x {secondaryVdiPath} -aoa -o{extractionPathHost}\\logs {hash_value}.pml''')
        os.system(f'''"{zipPath}" x {secondaryVdiPath} -aoa -o{extractionPathHost}\\density\\before {hash_value}_before.txt''')
        os.system(f'''"{zipPath}" x {secondaryVdiPath} -aoa -o{extractionPathHost}\\density\\after {hash_value}_after.txt''')

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
        retryHash(hashFilePath, ransomwareExtension, hash_value)
        deleteHash(hashFilePath, hashFileName, ransomwareExtension)
        continue

#hash_value = "3137413d086b188cd25ad5c6906fbb396554f36b4444441d5cff5a2176c28dd29fb0a"
# ans = os.system(f'''VBoxManage guestcontrol "{vmName}" run --exe {cmdPath} --username "{username}" --password {password} -- {cmdPath} /c "bazaar init {BazaarApiKey}" ''')
# ans = os.system(f"VBoxManage startvm {vmName}")
# # # ans = os.system(f'''VBoxManage guestcontrol "{vmName}" run --exe {cmdPath} --username "{username}" --password {password} -- {cmdPath} /c "bazaar download {hash_value} --unzip --output {ransomwareDownloadPath}\\{hash_value}.exe" ''')
# print(ans)
#vboxManage(procmonPath, f'''/AcceptEula /Nofilter /Quiet /BackingFile "{ransomwareDownloadPath}\\{hash_value}.PML" /Runtime {ransomwareExecTime}''', "start")
# bazaar download 8d2f2ee24882afe11f50e3d6d9400e35fa66724b321cb9f5a246baf63cbc1788 --unzip --output C:\\Users\\ransomware\\Downloads\\8d2f2ee24882afe11f50e3d6d9400e35fa66724b321cb9f5a246baf63cbc1788.exe
# bazaar init 82ea76c5b51d6e9ea0b08dba6a18771e
# tasklist /FI "IMAGENAME eq Procmon64.exe"
#VBoxManage guestcontrol "ransomware2" run --exe C:\Windows\System32\cmd.exe --username "ransomware" --password helloworld -- C:\Windows\System32\cmd.exe /c "E:\\densityscout_build_45_windows\\win64\\densityscout.exe -d -r -o E:\\density.txt C:\\Users\ransomware\\Desktop"