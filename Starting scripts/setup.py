import os, subprocess
homeFolder = os.path.expanduser('~')
loadedPathInfo=False
def getPath(prompt):
	thePath=input(prompt).strip().replace("\\","")
	if thePath[-1]!="/":
		thePath+="/"
	return thePath


try:
	from path_info import * 			# Set up where to find the relevant files
except:
	loadedPathInfo=False
if not loadedPathInfo:
	cwd = os.getcwd()
	# Opening a file
	file1 = open('path_info.py', 'w')
	cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews': ").strip()
	cprLocation=cprLocation.replace("CanvasPeerReviews/CanvasPeerReviews","CanvasPeerReviews")
	while not os.path.isdir(cprLocation):
		print(f"Unable to find '{cprLocation}'")
		cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews': ").strip()
	cprLocation=cprLocation[:-1]

	dataLocation=getPath("Enter the absolute path where the data should go.  A 'Data' directory will be created here if it doesn't exist: ").strip()
	while not os.path.isdir(dataLocation):
		print(f"Unable to find '{dataLocation}'")
		dataLocation=getPath("Enter the absolute path of the 'Data' folder, for instance '/Documents/MyCourse/PeerReviews': ").strip()

	if not os.path.exists(dataLocation + "Data"):
		print("Making Data directory")
		os.mkdir(dataLocation + "Data")
	else:
		print("Found data directrory")
	dataDirectory=dataLocation + "Data/"
	relDataDirectory=os.path.abspath(dataDirectory).replace(homeFolder,"")
	relCprLocation=os.path.abspath(cprLocation).replace(homeFolder,"")

	msg=f"import sys, os\n"
	msg+=f"os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from\n"
	msg+=f"homeFolder = os.path.expanduser('~')				  # get the home folder\n"
	if homeFolder in cprLocation:
		msg+=f"sys.path.insert(0, homeFolder + '{relCprLocation}')	# Use this if you are running on multiple machines with different absolute paths\n"
	else:
		msg+=f"sys.path.insert(0, '{cprLocation}')	# Use this if you are running on multiple machines with different absolute paths\n"
	if homeFolder in dataDirectory:
		msg+=f"RELATIVE_DATA_PATH='{relDataDirectory}' #data directory relative to the home folder where your class data will be stored\n"
		msg+="DATADIRECTORY=homeFolder  + RELATIVE_DATA_PATH\n"
	else:
		msg+=f"DATADIRECTORY='{dataDirectory}' #data directory relative to the home folder where your class data will be stored\n"
	msg+="loadedPathInfo=True\n"
	
	file1.write(msg)
	file1.close()
	subprocess.call(('open', 'path_info.py'))
	print(f"wrote file {cwd}/path_info.py, please edit with the location of files on your machine and then run setup.py again.")
	exit()
print()
print("The path_info.py file was read in with the following values: ")
print(f"	{homeFolder=}")
print(f"	{RELATIVE_DATA_PATH=}")
print(f"	{DATADIRECTORY=}")

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

print()
print("Congratulations - you are all set up.  You can now run any of the canvas peer review scripts")
print()
