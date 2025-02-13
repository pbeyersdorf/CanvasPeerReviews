import os, sys
from glob import glob

std="/".join(__file__.split("/")[:-1])
cwd=std + "/Peer Reviews"

#make the working directory
os.system(f"mkdir '{cwd}'")
os.chdir(cwd)

#create virtual environment
if not os.path.exists(f"{cwd}/venv"):
	print("Creating virtual environemnt venv")
	os.system(f"python3 -m venv '{cwd}/venv'")

#activate virtual environment
if sys.prefix == sys.base_prefix: #If not running from virtual environment
	os.system(f"cd '{std}'; source  'Peer Reviews/venv/bin/activate'; python3 install.py ")
	sys.exit()

#access github and download the files
os.system("pip install requests")
import requests, zipfile, io
from glob import glob
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

homeFolder = os.path.expanduser('~')
RELATIVE_DATA_PATH=f'{cwd}/Data/'.replace(homeFolder,"")
msg= f'''import sys, os
homeFolder = os.path.expanduser('~')
os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from
sys.path.insert(0, '{cwd}/cpr') # another location for the module files.
RELATIVE_DATA_PATH='{RELATIVE_DATA_PATH}' #data directory relative to the home folder where class data will be stored
DATADIRECTORY=homeFolder + RELATIVE_DATA_PATH
'''
file1.write(msg)
file1.close()

#install the required packages and set up aliases
os.system(f"cd '{cwd}'; pip install -r '{cwd}/requirements.txt'")
cmd=f'''echo "alias cpr='cd '{cwd}';source  '{cwd}/venv/bin/activate';python3 menu.py'" >> ~/outputFile'''
zshCmd=cmd.replace("outputFile", ".zshrc")
bashCmd=cmd.replace("outputFile", ".bashrc")
os.system(bashCmd)
os.system(zshCmd)
os.system(f"cd {cwd}/; python3 'menu.py'")
print("an alias has been set up so that you can type 'cpr' into the terminal to open the menu.")
exit()