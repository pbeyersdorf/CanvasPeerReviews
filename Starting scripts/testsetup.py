import os, subprocess
cwd = os.getcwd()
# Opening a file
file1 = open('path_info.py', 'w')
def getPath(prompt):
	thePath=input(prompt).strip().replace("\\","")
	if thePath[-1]!="/":
		thePath+="/"
	return thePath


cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews': ").strip()
while not os.path.isdir(cprLocation):
	print(f"Unable to find '{cprLocation}'")
	cprLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews': ").strip()

dataLocation=getPath("Enter the absolute path where the data should go.  A 'Data' directory will be created here if it doesn't exist: ").strip()
while not os.path.isdir(cprLocation):
	print(f"Unable to find '{cprLocation}'")
	dataLocation=getPath("Enter the absolute path of the 'CanvasPeerReviews' folder, for instance '/Documents/GitHub/CanvasPeerReviews': ").strip()

if not os.path.exists(dataLocation + "Data"):
	print("Making Data directory")
	os.mkdir(dataLocation + "Data")
else:
	print("Found data directrory")

exit()

msg= '''import sys, os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # work in the path the script was run from
homeFolder = os.path.expanduser('~')				  # get the home folder 
sys.path.insert(0, homeFolder + '/Documents/GitHub/CanvasPeerReviews')	# location of the module files.  Only necessary if they are stored somewhere other than the scripts
RELATIVE_DATA_PATH='/Nextcloud/Phys 51/CanvasPeerReviews/Data/' #data directory relative to the home folder where your class data will be stored
DATADIRECTORY=homeFolder  + RELATIVE_DATA_PATH'''
file1.write(msg)
file1.close()
subprocess.call(('open', 'path_info.py'))
print(f"wrote file {cwd}/path_info.py, please edit with the location of files on your machine and then run setup.py again.")
exit()