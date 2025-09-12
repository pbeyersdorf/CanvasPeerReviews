#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

activeAssignment=chooseAssignment(requireConfirmation=False, defaultAssignment=lastAssignment)
val=input("\nstudent name to check reviews on, or <enter> for a list of students: ")
s=selectStudentByName(val)

fileName=status['dataDir'] + status['prefix']+"_reviews_log.txt"
#fileName='/Users/peteman/Nextcloud/Peer Review Share/Jacob_Phys_50_(F25)/Data/course_1610911_reviews_log.txt'
f = open(fileName, "r")
lines = f.readlines()
f.close()
msg=f"Report on peer review completions by {s.name} on {activeAssignment.name}\n"
for lineNum, line in enumerate(lines):
	line=line
	if line.startswith("----"):
		thisMsg1="As of " + line.replace("----","").replace("\n"," ")
	if line.startswith(s.name):
		thisMsg=line
		lineNum+=1
		while lines[lineNum].startswith("\t"):
			if lines[lineNum].strip()!="":
				thisMsg+=lines[lineNum]
			lineNum+=1
		if not thisMsg in msg:
			msg+=thisMsg1+thisMsg
print(msg)