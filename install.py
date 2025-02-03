import os
os.system("pip install requests")

import requests, zipfile, io
from glob import glob

cwd="/".join(__file__.split("/")[:-1])
cwdFiles = [y for x in os.walk(cwd) for y in glob(os.path.join(x[0], '*'))]
if len(cwdFiles)>1:
	print('''
Place the install.py file in an empty directory that it can install 
into before running.  You will go to this directory to run the scripts, 
and once you install into it you should not move or rename it.
''')
	exit()

#download and extract the zip archive from github
zip_file_url="https://github.com/pbeyersdorf/CanvasPeerReviews/archive/refs/heads/main.zip"
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(cwd)

#move files into the parent directory
os.system(f"cd '{cwd}/CanvasPeerReviews-main/'; mv * ../")
os.system(f"rm -rf '{cwd}/CanvasPeerReviews-main'")
os.system(f"cd '{cwd}/Starting scripts/'; mv * ../")
os.system(f"rm -rf '{cwd}/Starting scripts'")

#write the path_info.py file
file1 = open(f'{cwd}/path_info.py', 'w')
msg= f'''import sys, os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from
sys.path.insert(0, '{cwd}/cpr') # another location for the module files.
DATADIRECTORY="./Data/"
'''
file1.write(msg)
file1.close()
os.system("cd '{cwd}'; pip install -r requirements.txt")
os.system("python3 'menu.py'")
exit()