This repo contains the code that was used to generate the provenance data at:
DOI_FILLIN

Published the the CST'23 FILLIN

Broadly, the code can be used to download batches of malware samples from [MalwareBazaar](https://bazaar.abuse.ch/), run them in a windows virtual machine and extract procmon logs provided as  input to [SPADE](https://github.com/ashish-gehani/SPADE).  The code depends on two virtual machine images: 1) `ransomwareVm.ova` - a windows 10 snapshot that has been prepared (procmon running etc.) to run a ransomware sample and 2) `spadeVm.ova` - a Ubuntu XXX image that has takes the output from the windows image and transforms it into a graphviz "dot" file. These images are available upon request to the author. The basic instructions to start running are:

1. run setup.py, this will import the two images into virtualbox and make snapshots of them
2. use the supplied "vm_hashes_exe.txt" file, a list of malware sha256 hashes from MalwareBazaar (this can be easily updated using Malware Bazaar's csv download)
3. run vmAutomation.py to collect logs, file-operations, densities, and screenshots for each hash in the previous step
4. run csv_populate to generate a summary of the dataset


# Requirements
ransomeware vm requirments:
Ram : 8gb
Processor : 1 core
Storage: 68gb

spade vm requirments:
Ram : 32gb
Processor: 2 cores
Storage : 50gb

Note: To change the settings of any vm, first make the desired changes then delete the current snapshot and take a new snapshot with same name.

# vmAutomation.py
This script will read a new line delimeted list of sha256 hashes from the file "hashes_exe.txt", download the corresponding binary from MalwareBazaar,  run the binary in the ransomewareVm and log its activity using ProcMon and 
then extract the logs and densities of desktop files to log.txt and density folder respectively.
It will then take the pml log files from the folder logs and will convert them into xml format using ProcMon filter then runs the script getFileOperations.py

# getFileOperations.py
This script runs in spadeVm and take xml logs from the main folder which is also a shared folder between 
host and spadeVm. The script then runs bash script file_ops.sh within the spadeVm which uses SPADE to
calculate the file operations done by the ransomware.

# csv_populate.py
#This script extracts the maximum density changed from densities, number of new files, and file operations
of a ransomware and add that data to the summary.csv file




