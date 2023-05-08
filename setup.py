import os
import configuration as config

os.system('''SET PATH=%PATH%;"C:\Program Files\Oracle\VirtualBox"''')

os.system(f'''VBoxManage import "{config.current_directory}\\spadeVm.ova"''')
os.system(f'''VBoxManage snapshot "{config.spadeVmName}" take "{config.spadeVmSnapshot}"''')

os.system(f'''VBoxManage import "{config.current_directory}\\ransomwareVm.ova"''')
os.system(f'''VBoxManage snapshot "{config.vmName}" take "{config.snapshotName}"''')

print("setup done")
