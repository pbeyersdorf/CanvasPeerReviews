#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

import hashlib

#Get all files
cprPath="/".join(utilities.__file__.split("/")[:-1])
gitHubPath='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/main/cpr'
gitHubPath2='https://raw.githubusercontent.com/pbeyersdorf/CanvasPeerReviews/refs/heads/main'

def git_blob_hash(file):
	#returns the hash of a local file, can be compared to the hash of the files stored on github  to determine if the file has changed.  To get the github hases
	with open(file, 'rb') as file_for_hash:
		data = file_for_hash.read()
    if isinstance(data, str):
        data = data.encode()
    data = b'blob ' + str(len(data)).encode() + b'\0' + data
    h = hashlib.sha1()
    h.update(data)
    return h.hexdigest()

def listOutdatedFiles(files):
	#not yet implemented
	url="https://api.github.com/repos/pbeyersdorf/CanvasPeerReviews/git/trees/main?recursive=1"
	resp = requests.get(url)
	githubData= eval(resp.text.replace("false","False").replace("true","True"))
	tree=githubData['tree']
	gitShasAndFiles=[{"sha": b['sha'], "path":b['path'].replace("Starting scripts/","")} for b in tree]
	gitShas=[b['sha'] for b in tree]
	localShasAndFiles={file: {"sha": git_blob_hash(file), "path":file, "fileName": file.split("/")[-1]} for file in files}	
	localFileNames=[file.split("/")[-1] for file in files]
	gitHubFileNames=[saf['path'].split("/")[-1] for saf in gitShasAndFiles]
	commonFileNames=list(set(localFileNames) & set(gitHubFileNames))
	return [file for file in files if localShasAndFiles[file]["sha"] not in gitShas and file.split("/")[-1] in commonFileNames]


def listOutdatedFilesSlow(files):
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

def addTemplates():
	templateDir=[x for x in txtFiles if "cpr/templates" in x][0].split("cpr/templates")[0]+"cpr/templates/"
	templateFileName=[y.replace(templateDir,"") for x in os.walk(templateDir) for y in glob(os.path.join(x[0], '*.txt'))]
	#https://api.github.com/repos/[USER]/[REPO]/git/trees/[BRANCH]?recursive=1
	url="https://api.github.com/repos/pbeyersdorf/CanvasPeerReviews/git/trees/main?recursive=1"
	resp = requests.get(url)
	githubData= eval(resp.text.replace("false","False").replace("true","True"))
	for b in  githubData['tree']:
		if "cpr/templates/" in b['path'] and ".txt" in b["path"]:
			fileName=b['path'].replace("cpr/templates/","")
			if (fileName not in templateFileName):
				fileUrl=f"{gitHubPath2}/cpr/templates/{fileName}".replace(" ","%20")
				templateContent = requests.get(fileUrl).text
				try:
					f = open(f"{templateDir}{fileName}" ,'w')
					f.write(templateContent)
					f.close()
					print(f"Adding template: {fileName}")
				except:
					print(f"Unable to create template '{file}'")

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
			try:
				f = open(file,'w')
				f.write(githubContent)
				f.close()
			except:
				print(f"Unable to overwrite, {file} is uncahnged")
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
addTemplates()
#if input(f"\nUpdate text files (such as from templates) (y/n)?").lower()=="y":
#	updateFiles(txtFiles)
outdatedScriptsFiles=listOutdatedFiles(scriptsFiles)
print(f"\nThere are {len(outdatedScriptsFiles)} differing starting script files.")
if len(outdatedScriptsFiles)>0:# and input(f"Update starting scripts (y/n)?").lower()=="y":
	updateFiles(outdatedScriptsFiles)

