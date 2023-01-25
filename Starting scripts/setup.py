import os, subprocess

loadedPathInfo=False
while not loadedPathInfo:
	try:
		from path_info import * 			# Set up where to find the relevant files
		loadedPathInfo=True
	except:
		cwd = os.getcwd()
		# Opening a file
		file1 = open('path_info.py', 'w')
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
except:
	sys.stdout = sys.__stdout__ #turn output back on
	input("Unable to import CanvasPeerReviews.  Make sure the path is set correclty in path_info.py then run setup.py again.")
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
finish(True)

print()
print("Congratulations - you are all set up.  You can now run any of the canvas peer review scritps")
print()
