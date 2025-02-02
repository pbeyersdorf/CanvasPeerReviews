#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#Get all files
cprPath="/".join(utilities.__file__.split("/")[:-1])
gitHubPath='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/main/cpr'
gitHubPath2='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/refs/heads/main'

def updateFiles(files):
	val="n"
	for file in files:
		if file in scriptsFiles:
			#fileName=file.split("/")[-1]
			relPath=file.replace(cwd,"")
			url=f"{gitHubPath2}/Starting scripts{relPath}".replace(" ","%20")
		else:
			url=file.replace(cprPath,gitHubPath).replace(" ","%20")
		resp = requests.get(url)
		if resp.status_code!=200:
			print(f"Failed to download {url} with status code {resp.status_code}…")
			continue	
		if val!=val.upper():
			val = input(f"Overwrite {file} (y/N)?")
		if val.lower()=="y":
			f = open(file,'w')
			f.write(resp.text)
			f.close()
		elif val=="N":
			return

import os
from glob import glob
import requests
cwd= ("/").join(__file__.split("/")[:-1])
pyFiles = [y for x in os.walk(cprPath) for y in glob(os.path.join(x[0], '*.py'))]
txtFiles = [y for x in os.walk(cprPath) for y in glob(os.path.join(x[0], '*.txt'))]
scriptsFiles= [y for x in os.walk(cwd) for y in glob(os.path.join(x[0], '*.py'))]

print('''
This script will access the latest files in the 'CanvasPeerReviews' 
repository on github, and give you the option to use them to overwrite the
existing files on your computer.  There are three categories of files:
	
	Core python files from the cpr package
	Text files used as templates
	Starting scripts that you interact with 
''')

if input(f"Update core python files (y/n)?").lower()=="y":
	updateFiles(pyFiles)
if input(f"\nUpdate text files (such as from templates) (y/n)?").lower()=="y":
	updateFiles(txtFiles)
if input(f"\nUpdate starting scripts (y/n)?").lower()=="y":
	updateFiles(scriptsFiles)

