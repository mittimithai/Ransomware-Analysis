import os
import subprocess
import csv

density_path = "E:\\extraction\\density"
file_ops_path = "E:\\extraction\\file_ops"
csv_file_path = "E:\\extraction\\summary.csv"
sampleDensityPath = "E:\\extraction\\sampleDensity.txt"
cols = ['SHA256', 'FileOperations', 'DeltaDensity', 'NewFiles']
print(cols)
rows = [cols]

def getDeltaDensity(before, after):

    unchanged_entropy = {}
    changed_entropy = {}
    new_files = {}

    files_changed = False

    '''
    take only file name and make sure they are not same cuz this is in our control
    check number of files in original and dictionary to make sure there is no key duplication
    '''
    try:
        with open(before, 'r') as beforeDensityFile:
            beforeDensity = [each.strip() for each in beforeDensityFile.readlines()]
    except:
        with open(sampleDensityPath, 'r') as beforeDensityFile:
            beforeDensity = [each.strip() for each in beforeDensityFile.readlines()]

    try:
        with open(after, 'r', encoding='utf-8') as afterDensityFile:
            afterDensity = [each.strip() for each in afterDensityFile.readlines()]
    except:
        afterDensity = []

    for file in beforeDensity:
        density, filename = file.split("|")
        filename = filename.split(".")[0]
        unchanged_entropy[filename] = density

    for file in afterDensity:
        try:
            density, filename = file.split("|")
            filename = filename.split(".")[0]
        except:
            return 0, 0


        if filename not in unchanged_entropy.keys():
            new_files[filename] = density

        elif unchanged_entropy[filename] != density:
            changed_entropy[filename] = abs(float(density)-float(unchanged_entropy[filename]))
            files_changed = True
    
    if len(changed_entropy) == 0:
        delta_density = 0
    else:
        delta_density = max(changed_entropy.values())

    numberNewFiles = len(new_files.items())
    return delta_density, numberNewFiles

fileOpsFile = open (file_ops_path, "r")
fileOpsList = fileOpsFile.readlines()

for line in fileOpsList:
    file_ops = line.split(" ")[0]
    ransomware = line.split(" ")[1].split("/")[-1].split(".")[0]
    before = f"{density_path}\\before\\{ransomware}_before.txt"
    after = f"{density_path}\\after\\{ransomware}_after.txt"
    deltaDensity, numberNewFiles = getDeltaDensity(before, after)
    print(ransomware, file_ops, deltaDensity, numberNewFiles)
    rows.append([ransomware, file_ops, deltaDensity, numberNewFiles])
fileOpsFile.close()

#open the file in the write mode
with open(csv_file_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(rows)