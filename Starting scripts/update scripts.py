#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#Get all files
cprPath="/".join(utilities.__file__.split("/")[:-1])
gitHubPath='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/main/cpr'
gitHubPath2='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/refs/heads/main'

def listOutdatedFiles(files):
	changedFiles=[]
	for file in files:
		fileName=file.split("/")[-1]
		if file in scriptsFiles:
			relPath=file.replace(cwd,"")
			url=f"{gitHubPath2}/Starting scripts{relPath}".replace(" ","%20")
		else:
			url=file.replace(cprPath,gitHubPath).replace(" ","%20")
		resp = requests.get(url)
		githubContent=resp.text
		f = open(file,'r')
		existingContent=f.read()
		f.close()	
		#print(f"checking {fileName}" , end="\r")
		printLine(msg=f"checking {fileName}", newLine=False)
		if (resp.status_code==200 and existingContent!=githubContent):
			changedFiles.append(file)
	printLine(msg="", newLine=True)
	return changedFiles


def updateFiles(files):
	val="n"
	msg=""
	for file in files:
		fileName=file.split("/")[-1]
		if file in scriptsFiles:
			relPath=file.replace(cwd,"")
			url=f"{gitHubPath2}/Starting scripts{relPath}".replace(" ","%20")
		else:
			url=file.replace(cprPath,gitHubPath).replace(" ","%20")
		resp = requests.get(url)
		githubContent=resp.text
		if resp.status_code!=200:
			msg+=(f"Failed to download {url} with status code {resp.status_code}\n")
			continue	
		if val!=val.upper():
			val = input(f"Overwrite {file} (y/N)?")

		if val.lower()=="y":
			f = open(file,'w')
			f.write(githubContent)
			f.close()
		elif val=="N":
			print(msg)	
			return
	print(msg)	

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
existing files on your computer.  There are two categories of files:
	
	Core python files from the cpr package
	Starting scripts that you interact with 
''')

outdatedPyFiles=listOutdatedFiles(pyFiles)
print(f"There are {len(outdatedPyFiles)} differing core python files.")
if len(outdatedPyFiles)>0:# and input(f"Update core python files (y/n)?").lower()=="y":
	updateFiles(outdatedPyFiles)
print()
#if input(f"\nUpdate text files (such as from templates) (y/n)?").lower()=="y":
#	updateFiles(txtFiles)
outdatedScriptsFiles=listOutdatedFiles(scriptsFiles)
print(f"\nThere are {len(outdatedScriptsFiles)} differing starting script files.")
if len(outdatedScriptsFiles)>0:# and input(f"Update starting scripts (y/n)?").lower()=="y":
	updateFiles(outdatedScriptsFiles)

