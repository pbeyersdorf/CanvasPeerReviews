import sys, os, subprocess, pathlib, time
from tkinter import *
from tkinter import filedialog
from html import escape
#hidden imports
import readchar

from pathlib import Path
python_exe = str(Path(sys.executable).with_stem("python").resolve())
starting_path = str((Path(__file__)).resolve())
scripts_path = str((Path(__file__).parent / "scripts").resolve())
DATADIRECTORY = str((Path(__file__).parent.parent / "data").resolve())
print(f"{DATADIRECTORY=}")
credentials_file = str((Path(__file__).parent.parent / "credentials.py").resolve())

#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews
status['fromPyInstall']=True


def menu():
	#put in .zshrc 
	#alias cpr='cd /Users/peteman/Nextcloud/Phys\ 51/Grades/CanvasPeerReviews; python menu.py'
	complete=False
	relPath="."
	relPath=scripts_path
	theFile=""
	
	if os.path.isfile(credentials_file):
		credentials=str(open(credentials_file).read())
		print()
		print(credentials)
		print()
		exec(credentials, globals(), locals())
		print("read and executed credentials file")
		print(f"{COURSE_ID=}")
		print(f"{CANVAS_URL=}")
		
	else:
		print("unable to read credentials file")

	
	print()
	while theFile=="":
		files=[file for file in os.listdir(relPath) if ".py" in file and "menu" not in file and ".pyc" not in file and "credentials" not in file and "(conflicted" not in file and "shell.py" not in file and "path_info.py" not in file]
		folders=[item for item in os.listdir(relPath) if os.path.isdir(os.path.join(os.path.abspath(relPath), item)) and "__pycache__" not in item and relPath!=item[0] and "Data" not in item]
		files.sort()
		folders.sort()
		if relPath==scripts_path:
			print("\t"+str(0) + ") python shell")
		else:
			print("\t"+str(0) + ") <- go back")
			
		for i,file in enumerate(files):
				print("\t"+str(i+1) + ") " + file.replace(".py",""))
		for j,folder in enumerate(folders):
				print("\t"+str(j+i+2) + ") " + folder + "...")
		print()
		val=int(input("which program do you want to run?  "))-1
		if val<0 and relPath==scripts_path:
			theFile=relPath+"/shell.py"
		elif val<0:
			relPath="/".join(relPath.split("/")[:-1])
			print("\n\nlooking in " + relPath)
		elif val > i:
			relPath+="/"+folders[val-i-1] 
			print("\n\nlooking in " + relPath)
		else:
			theFile=relPath+"/"+files[val]
	
	if relPath!=scripts_path:
		cmd='cp credentials.py "' + relPath +'/"'
		os.system(cmd)
		cmd='cp "path_info.py" "' + relPath +'/"'
		os.system(cmd)
	
	exec(open(theFile).read())
	if relPath!=scripts_path:
		cmd='rm "' + relPath +'/credentials.py"'
		os.system(cmd)
		cmd='rm "' + relPath +'/path_info.py"'
		os.system(cmd)

#check if there is a credentials file
print("looking for: " +  credentials_file)
if os.path.isfile(credentials_file):
	print("found credentials file")
	menu()
else:
	print("unable to find credentials file")
	setupFile=scripts_path +'/setup class.py'
	exec(open(setupFile).read())
	
finish(True)
import code
code.interact(local=globals())
