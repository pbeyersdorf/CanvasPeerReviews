import os, subprocess
homeFolder = os.path.expanduser('~')
loadedPathInfo=False
def getPath(prompt, defaultPath=None):
	if defaultPath!=None:
		thePath=input(f"{prompt} [{defaultPath}]: ").strip().replace("\\","")
		if thePath=="":
			thePath=defaultPath
	else:
		thePath=input(f"{prompt}: ").strip().replace("\\","")
	if thePath[-1]!="/":
		thePath+="/"
	return thePath


try:
	from path_info import * 			# Set up where to find the relevant files
except:
	loadedPathInfo=False
while not loadedPathInfo:
	cwd = os.getcwd()
	# Opening a file
	file1 = open('path_info.py', 'w')
	msg=f"import sys, os\n"
	msg+=f"os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from\n"
	msg+=f"homeFolder = os.path.expanduser('~')				  # get the home folder\n"
	
	reUseCPRPath=True
	try:
		from CanvasPeerReviews import *		
	except Exception as error:
		if "CanvasPeerReviews" in str(error):
			reUseCPRPath=False
			cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews'").strip()
			cprLocation=cprLocation.replace("CanvasPeerReviews/CanvasPeerReviews","CanvasPeerReviews")
			while not os.path.isdir(cprLocation):
				print(f"Unable to find '{cprLocation}'")
				cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews'").strip()
	if reUseCPRPath:
		for itm in sys.path:
			if "CanvasPeerReviews" in itm:
				cprLocation=itm +"/"
			
	cprLocation=cprLocation[:-1]
	relCprLocation=os.path.abspath(cprLocation).replace(homeFolder,"")
	if homeFolder in cprLocation:
		msg+=f"sys.path.insert(0, homeFolder + '{relCprLocation}')	# Use this if you are running on multiple machines with different absolute paths\n"
	else:
		msg+=f"sys.path.insert(0, '{cprLocation}')	# Use this if you are running on multiple machines with different absolute paths\n"

	defaultLocation=os.path.dirname(os.path.realpath(__file__))
	dataLocation=getPath(f"Enter the absolute path where the data should go.  A 'Data' directory will be created here if it doesn't exist", defaultLocation).strip()
	if dataLocation=="":
		dataLocation=defaultLocation
	while not os.path.isdir(dataLocation):
		print(f"Unable to find '{dataLocation}'")
		dataLocation=getPath("Enter the absolute path of the 'Data' folder, for instance '/Documents/MyCourse/PeerReviews'").strip()

	if not os.path.exists(dataLocation + "Data"):
		print("Making Data directory")
		os.mkdir(dataLocation + "Data")
	else:
		print("Found data directrory")
	dataDirectory=dataLocation + "Data/"
	relDataDirectory=os.path.abspath(dataDirectory).replace(homeFolder,"")

	if homeFolder in dataDirectory:
		msg+=f"RELATIVE_DATA_PATH='{relDataDirectory}' #data directory relative to the home folder where your class data will be stored\n"
		msg+="DATADIRECTORY=homeFolder  + RELATIVE_DATA_PATH\n"
	else:
		msg+=f"DATADIRECTORY='{dataDirectory}' #data directory relative to the home folder where your class data will be stored\n"
	msg+="loadedPathInfo=True\n"
	print(msg)
	file1.write(msg)
	file1.close()
	subprocess.call(('open', 'path_info.py'))
	input(f"wrote file {cwd}/path_info.py, please edit with the location of files on your machine and then hit enter to continue: ")
	from importlib import reload
	import path_info
	reload(path_info)
	from path_info import *
	#exit()
print()
try:
	print("The path_info.py file was read in with the following values: ")
	print(f"	{homeFolder=}")
	print(f"	{RELATIVE_DATA_PATH=}")
	print(f"	{DATADIRECTORY=}")
except:
	pass

importedCanvasPeerReviews=False
try:
	sys.stdout = open(os.devnull, 'w') #turn off output
	from CanvasPeerReviews import *		# the main module for managing peer reviews
	importedCanvasPeerReviews=True
	sys.stdout = sys.__stdout__ #turn output back on
except ModuleNotFoundError as err:
	sys.stdout = sys.__stdout__ #turn output back on
	print(err)
	if 'CanvasPeerReviews' in str(err):
	    print(" Make sure the path is set correclty in path_info.py then run setup.py again.")
	exit()
print()
print("The CanvasPeerReviews module was imported correctly")
print()

status['setup']=True
students, graded_assignments, lastAssignment = initialize()

print()
print("The course was initialized successfully.  Now lets setup the grading parameters.  If you don't want to do this now you can ctrl-c to exit and you will be prompted for these parameters the next time you run any canvas peer review script")
print()

#################  Get relevant parameters assignment  #################
params=getParameters()

#################	Generate a class roster  #################
print("Let's get a roster complete with images of the students")
users = utilities.course.get_users(enrollment_type=['student'])
from html import escape
fileName=status['dataDir'] +  "roster.html"
f = open(fileName, "w")
f.write("<html><head><title>Roster for " + utilities.course.name + " </title><style>\n")
f.write("a {text-decoration:none}\n")
f.write("</style><meta http-equiv='Content-Type' content='text/html; charset=utf-16'></head><body>\n")
f.write("<h3>Roster for  "+utilities.course.name +"</h3>\n<table>\n")

for u in users:
	name=u.name
	url= u.get_profile()['avatar_url']
	email=u.email
	printLine("getting avatar for " + name, False)
	f.write("<tr><td><img src='" +url+ "'>\n<a href='mailto:" + email + "'>" + name +"</a></td></tr>")
f.write("</table></body></html>\n")
f.close()
subprocess.call(('open', fileName))
finish(True)

aliasExists=False
try:
	f = open(homeFolder +"/.profile","r")
	lines = f.readlines()
	f.close()
	aliasExists = "cpr=" in str(lines)
except:
	pass
if not aliasExists:
	f = open(homeFolder +"/.profile","a")
	f.write(f"alias cpr='cd \"{os.path.dirname(os.path.realpath(__file__))}\"; python3 menu.py'")
	f.close()
	print("Added an alias 'cpr' to .profile")
	
print()
print("Congratulations - you are all set up.  You can now run any of the canvas peer review scripts: ")
print()
returnVal=os.system("python3 -i 'menu.py'")
