1. The current directory is called the main folder which should be named 'extraction'
2. run setup.py, this will import the vms into your virtualbox and make snapshots of them
3. put SHA256 hashes in vm_hashes_exe
3. run vmAutomation.py to collect logs, file-operations, densities, and screenshots
4. run csv_populate to generate summary of dataset

#vmAutomation.py
This script will read SHA56 Hashes from the file "hashes_exe.txt", 
run the ransomware sample in the ransomewareVm and log its activity using ProcMon and 
then extract the logs and density files to log.txt and density folder respectively
then take the pml log files from the folder logs and will convert them into xml format using ProcMon filter
then runs the script getFileOperations.py

#csv_populate.py
#This script extracts the maximum density changed from densities, number of new files, and file operations
of a ransomware and add that data to the summary.csv file

#getFileOperations.py
This script runs in spadeVm and take xml logs from the main folder which is also a shared folder between 
host and spadeVm. The script then runs bash script file_ops.sh within the spadeVm which uses SPADE to
calculate the file operations done by the ransomware.

ransomeware vm requirments:
Ram : 8gb
Processor : 1 core
Storage: 68gb

spade vm requirments:
Ram : 32gb
Processor: 2 cores
Storage : 50gb

Note: To change the settings of any vm, first make the desired changes then delete the current snapshot and take a new snapshot with 
same name.

