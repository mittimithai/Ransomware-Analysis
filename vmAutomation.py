import sys
import os
import time
from sys import exit
from tqdm import tqdm
import signal
import configuration as config
import threading


# function to run a command in vm
def vboxManage(programPath, programArg, cmdType):
    count = 0
    while(1):
        output = os.system(f'''VBoxManage guestcontrol "{config.vmName}" {cmdType} --exe {programPath} --username "{config.username}" --password {config.password} -- {programPath} {programArg} ''')

        if programArg == f'''/c "{config.densityscoutPath} -d -r -o {config.densitySavingPath}\\densityAfter.txt {config.folderForDensity}" ''':
            return 
        
        if programArg == f'''/c move {config.densitySavingPath}\\densityAfter.txt {config.logsDumpVdiPathVm}\\{hash_value}_after.txt''':
            return
        
        if programArg == f'''/c move {config.densitySavingPath}\\densityBefore.txt {config.logsDumpVdiPathVm}\\{hash_value}_before.txt''':
            return
        
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

#function to read SHA256 hash from hashes file
def extrachHash(hashFilePath, hashFileName, ransomwareExtension):

    # check if there is any hash left in the file, otherwise close
    filesize = os.path.getsize(f"{hashFilePath}\\{hashFileName}")
    if filesize == 0:
        print('file is empty, no hash to read \n')
        sys.exit("file is empty, no hash to read")

    # read the hash from the file
    try:
        with open(f"{hashFilePath}\\{hashFileName}", 'r') as f:
            hash = f.readline()
            return hash.strip()

    except:
        print("Error: Unable to read the file")

#function to delete SHA56 hash from hashes file
def deleteHash(hashFilePath, hashFileName, ransomwareExtension):

    # check if there is any hash left in the file, otherwise close
    filesize = os.path.getsize(f"{hashFilePath}\\{hashFileName}")
    if filesize == 0:
        print('file is empty, no hash to delete \n')
        sys.exit("file is empty, no hash to delete")

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

                    # we want to remove 1st line
                    if ptr != 1:
                        fw.write(line)
                    ptr += 1
    except:
        print("Error:Unable to delete the hash")

#function to save the SHA56 hash to the hash_done file
def saveHash(hashFilePath, ransomwareExtension, hash_value):

    # save the hash to a new file
    try:
        with open(f"{hashFilePath}\\vm_hashes_done_{ransomwareExtension}.txt", 'a') as fw:
            fw.write(hash_value+'\n')
    except:
        print("Error:Unable to save the hash")

#function to save the SHA56 hash to the hash_retry file
def retryHash(hashFilePath, ransomwareExtension, hash_value):

    # save the hash to a new file
    try:
        with open(f"{hashFilePath}\\vm_hashes_retry_{ransomwareExtension}.txt", 'a') as fw:
            fw.write(hash_value+'\n')
    except:
        print("Error:Unable to save retry hash")

#function to timeout if procmon log is corrupt
def timeout():
    global pmlCorrupt
    count = 0
    while(pmlCorrupt !='no' and count != config.procmonTimeout):
        time.sleep(1)
        count +=1

    if pmlCorrupt == 'null':
        pmlCorrupt = 'yes'
        os.system('Taskkill /IM Procmon64.exe /F')

#function to setup spade vm and start it 
def runSpade():

    #makes the shared folder
    os.system(f'''VBoxManage snapshot {config.spadeVmName} restore {config.spadeVmSnapshot}''')
    os.system(f'''VBoxManage sharedfolder add "{config.spadeVmName}" --name "extraction" --hostpath "{config.sharedFolderPath}" --automount''')

    # starts the vm and sets up username and password
    print('\n')
    os.system(f"VBoxManage startvm {config.spadeVmName}")
    os.system(f'VBoxManage controlvm {config.spadeVmName} setcredentials {config.spadeVmUsername} {config.spadeVmPass} "DOMTEST"')
    for i in tqdm(range(config.spadeVmStartTime)):
            time.sleep(1)
    print('\n')

#function to close and restore spade vm
def closeSapde():

    print('\n')
    print('closing Spade VM \n')
    os.system(f"VBoxManage controlvm {config.spadeVmName} poweroff")
    time.sleep(config.spadeVmCloseTime)

#function to start vm
def startVm():
    os.system(f"VBoxManage startvm {config.vmName}")
    os.system(f'VBoxManage controlvm {config.vmName} setcredentials {config.username} {config.password} "DOMTEST"')
    for i in tqdm(range(config.vmStartTime)):
        time.sleep(1)
    print('\n')

#function to close vm
def closeVm():
    print('closing ransomeware VM \n')
    os.system(f"VBoxManage controlvm {config.vmName} poweroff")
    time.sleep(config.vmClosingTime)
    print('\n')

#variable to check if procmon log is corrupted or not
pmlCorrupt = ''

# counter to track number of iterations
count = 0

while(count != config.runs):
    pmlCorrupt = 'null'
    try:
        # starts the vm and sets up config.username and config.password
        startVm()

        # reads hash from the file and print it
        print("extracting hash from txt file \n")
        hash_value = extrachHash(config.hashFilePath, config.hashFileName, config.ransomwareExtension)
        print("Hash: ", hash_value, '\n')

        # calculating density prior
        print("calculating before density \n")
        vboxManage(config.cmdPath, f'''/c "{config.densityscoutPath} -d -r -o {config.densitySavingPath}\\densityBefore.txt {config.folderForDensity}" ''', "run")

        # downloads ransomware from bazaar api
        print("downloading ransomware \n")
        vboxManage(config.cmdPath, f'''/c "bazaar init {config.BazaarApiKey}" ''', "run")
        vboxManage(config.cmdPath, f'''/c "bazaar download {hash_value} --unzip --output {config.ransomwareDownloadPath}\\{hash_value}.{config.ransomwareExtension}" ''', "run")

        #opens procmon and start logging in a backing file
        print("ransomware downloaded, opening procmon \n")
        vboxManage(config.procmonPath, f'''/BackingFile {config.logSavingPathVm}\\{hash_value}.pml /NoFilter /AcceptEula /LoadConfig {config.ProcmonfilterFilePath} /Quiet''', "start")
        vboxManage(config.procmonPath, f'''/waitforidle ''', "run")

        # triggers ransomware
        print("procmon started, triggering ransomware \n")
        vboxManage(config.cmdPath, f'''/c "{config.ransomwareDownloadPath}\\{hash_value}.{config.ransomwareExtension}" ''', "start")

        # waiting for the ransomware to attack
        print("ransomware triggered, waiting for attack \n")
        for i in tqdm(range(config.ransomwareExecTime)):
            time.sleep(1)
        print('\n')

        #taking screenshot of the desktop
        os.system(f"VBoxManage controlvm {config.vmName} screenshotpng {config.sreenshotsPath}\\{hash_value}.png")
        print('screenshot of vm captured \n')

        #calculating density after
        print("calculating after density \n")
        vboxManage(config.cmdPath, f'''/c "{config.densityscoutPath} -d -r -o {config.densitySavingPath}\\densityAfter.txt {config.folderForDensity}" ''', "run")

        #closing procmon
        print('closing procmon \n')
        vboxManage(config.procmonPath, f'''/Terminate''', "start")
        time.sleep(180)

        #closing the vm
        print("Procmon closed, closing vm \n")
        closeVm()

        # mounting the secondary drive to move procmon logs to
        print("vm closed, mounting secondary drive to transfer logs \n")
        os.system(f'''VBoxManage storageattach {config.vmName} --storagectl SATA --port 3 --type hdd --medium "{config.secondaryVdiPath}" ''')

        # restarting the vm 
        print("drive mounted, starting vm")
        startVm()

        # emptying secondary storage and moving logs to secondary storage
        print("vm started, moving logs from vm to secondary storage \n")
        # vboxManage(config.cmdPath, f'''/c del F:\\*.pml''', "run")
        # vboxManage(config.cmdPath, f'''/c del F:\\*.txt''', "run")
        vboxManage(config.cmdPath, f'''/c del /Q F:\\*.*''', "run")

        vboxManage(config.cmdPath, f'''/c move {config.densitySavingPath}\\densityAfter.txt {config.logsDumpVdiPathVm}\\{hash_value}_after.txt''', "run")
        vboxManage(config.cmdPath, f'''/c move {config.densitySavingPath}\\densityBefore.txt {config.logsDumpVdiPathVm}\\{hash_value}_before.txt''', "run")
        vboxManage(config.cmdPath, f'''/c move {config.logSavingPathVm}\\{hash_value}.pml {config.logsDumpVdiPathVm}\\{hash_value}.pml''', "run")
        time.sleep(80)

        # closing vm
        print("logs moved, closing vm \n")
        closeVm()

        # unmounting the secondary drive
        print("vm closed, unmounting secondary drive \n")
        os.system(f"VBoxManage storageattach {config.vmName} --storagectl SATA --port 3 --medium none")

        # restoring the vm back to a fresh snapshot
        print("secondary drive unmounted \n")
        os.system(f'''VBoxManage snapshot {config.vmName} restore {config.snapshotName}''')
        print("snapshot restored \n")

        # extracting the logs and density file
        print('extracting logs from secondary storage to host \n')
        os.system(f'''"{config.zipPath}" x {config.secondaryVdiPath} -aoa -o{config.pmlPath} {hash_value}.pml''')
        os.system(f'''"{config.zipPath}" x {config.secondaryVdiPath} -aoa -o{config.density_path}\\before {hash_value}_before.txt''')
        os.system(f'''"{config.zipPath}" x {config.secondaryVdiPath} -aoa -o{config.density_path}\\after {hash_value}_after.txt''')
        print('\n')
        
        #starting timeout
        t1 = threading.Thread(target=timeout)
        t1.start()

        # converting pml log to xml
        print('extraction done, converting pml log into xml \n')
        os.system(f'''{config.procmonPathHost} /OpenLog {config.pmlPath}\\{hash_value}.PML /LoadConfig {config.ProcmonfilterFilePathHost} /SaveAs {config.xmlPath}\\{hash_value}.XML''' )
        
        if pmlCorrupt == 'yes':
            os.system(f'''del {config.pmlPath}\\*.pml''')
            os.system(f'''del {config.xmlPath}\\*.XML''')
            print('procmon log corrupted, cannot convert \n')
            raise Exception("Unable to execute the command")
        
        elif pmlCorrupt == 'null':
            pmlCorrupt = 'no'
            t1.join()

        #running spade vm and collecting file operations
        print('starting spadeVm to collect file operations \n')
        runSpade()
        os.system(f'''VboxManage guestcontrol "{config.spadeVmName}" run --exe {config.getFileOperationsPath} --username "{config.spadeVmUsername}" --password "{config.spadeVmPass}"''')
        closeSapde()
        print('\n file operations extracted \n')

        # saving the hash as done and deleting it from the original file and cleaning up xmls and pmls
        os.system(f'''del {config.xmlPath}\\*.XML''')
        os.system(f'''"{config.zipPath}" a -tzip {config.pmlDonePath}\\{hash_value}.zip {config.pmlPath}\\{hash_value}.PML -r0 && del {config.pmlPath}\\{hash_value}.PML''')
        saveHash(config.hashFilePath, config.ransomwareExtension, hash_value)
        deleteHash(config.hashFilePath, config.hashFileName, config.ransomwareExtension)
        
        count = count + 1
        print('runs done: ', count, '\n')

    # if hashfile is empty, close vms and restore snapshots
    except SystemExit:
        closeVm()
        os.system(f'''VBoxManage snapshot {config.vmName} restore {config.snapshotName}''')
        print("snapshot restored \n")
        os.system('Taskkill /IM Procmon64.exe /F')
        closeSapde()
        break

    # if keyboard interrupt, close vm and restore snapshot
    except KeyboardInterrupt:
        print('keyboard interrupt detected \n')
        closeVm()
        os.system(f'''VBoxManage snapshot {config.vmName} restore {config.snapshotName}''')
        print("snapshot restored \n")
        os.system('Taskkill /IM Procmon64.exe /F')
        closeSapde()
        break

    # if any other exception occured, close vm and resotre snapshot and restart the iteration
    except:
        print("Error: Exception occured \n")
        closeVm()
        os.system(f'''VBoxManage snapshot {config.vmName} restore {config.snapshotName}''')
        print("snapshot restored \n")
        os.system('Taskkill /IM Procmon64.exe /F')
        closeSapde()
        retryHash(config.hashFilePath, config.ransomwareExtension, hash_value)
        deleteHash(config.hashFilePath, config.hashFileName, config.ransomwareExtension)
        continue