import sys, os, subprocess, pathlib
from tkinter import *
from tkinter import filedialog

homeFolder = os.path.expanduser('~')

def clearOldContent():
	contentToDelete=["Data", "Data-backups", "path_info.py", "credentials.py"]
	itemsToDelete = [itm for itm in os.listdir() if itm in contentToDelete]
	if len(itemsToDelete)==0:
		return
	print(f"Go to '{pathlib.Path().resolve()}'\nand delete the following items to clear out old data:\n")
	for itm in 	itemsToDelete:
		print(f"\t{itm}")	
	input("\nWhen ready to proceed hit enter:")
	return

def getPath(prompt="Select directory", defaultPath="/"):
	print(prompt)
	root = Tk()
	root.withdraw()
	root.filename =  filedialog.askdirectory(initialdir = defaultPath, title = prompt)
	return root.filename + "/"

def getRelativeDataPath():
	defaultLocation=os.path.dirname(os.path.realpath(__file__))
	dataLocation=getPath(f"In the pop up window (which may be behind terminal) choose the folder where the data directory should go.  A 'Data' directory will be created here if it doesn't exist", defaultLocation)
	if not os.path.exists(dataLocation + "Data"):
		print("Making Data directory")
		os.mkdir(dataLocation + "Data")
	else:
		print("Found data directrory")
	dataDirectory=dataLocation + "Data//" # note sure why two slashes are necessary, but one seems to be stripped off
	relDataDirectory=os.path.abspath(dataDirectory).replace(homeFolder,"")
	return relDataDirectory

os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from
clearOldContent()
#sys.path.insert(0, homeFolder + '/Documents/GitHub/CanvasPeerReviews')	# location of the module files.  Only necessary if they are stored somewhere other than the scripts
RELATIVE_DATA_PATH=getRelativeDataPath() #data directory relative to the home folder where your class data will be stored


cwd = os.getcwd()
successfullImport=False	
attempt=0
while not successfullImport:
	attempt+=1
	if attempt>2:
		print("Giving up")
		exit()
	try:
		from cpr import *	
		successfullImport=True	
	except Exception as error:
		print(error)
		print("Unable to import CanvasPeerReviews, perhaps the wrong import path?")
		if "cpr" in str(error):
			cprLocation=getPath("In the pop up window (which may be behind terminal) choose the 'cpr' folder that contains the source code")
			cprLocation=cprLocation.replace("CanvasPeerReviews/CanvasPeerReviews","CanvasPeerReviews")
		cprLocation=cprLocation[:-1]
		print(f"adding {cprLocation} to sys.path")
		sys.path.insert(0, cprLocation)

file1 = open('path_info.py', 'w')
msg= f'''import sys, os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from
homeFolder = os.path.expanduser('~')				  # get the home folder
sys.path.insert(0, homeFolder + '/Documents/GitHub/CanvasPeerReviews') # one location of the module files
'''
if not successfullImport:
	msg+=f"sys.path.insert(0, '{cprLocation}') # another location for the module files."
if not os.path.exists(homeFolder + RELATIVE_DATA_PATH):
	msg+=f'''
DATADIRECTORY='{RELATIVE_DATA_PATH}' #data directory'''
else:
	msg+=f'''
RELATIVE_DATA_PATH='{RELATIVE_DATA_PATH}' #data directory relative to the home folder where class data will be stored
DATADIRECTORY=homeFolder + RELATIVE_DATA_PATH'''
file1.write(msg)
file1.close()



print()
print("The CanvasPeerReviews module was imported correctly")
print()

status['setup']=True
students, graded_assignments, lastAssignment = initialize(dataDirectory= homeFolder  + RELATIVE_DATA_PATH)

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
	try:
		url= u.get_profile()['avatar_url']
	except:
		url="https://brandslogos.com/wp-content/uploads/thumbs/san-jose-state-spartans-logo.png"
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
