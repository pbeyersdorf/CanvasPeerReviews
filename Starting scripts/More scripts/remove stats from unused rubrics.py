#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

for cid in criteriaDescription:
	print(cid, criteriaDescription[cid])
cid=""
while not cid in criteriaDescription:
	cid=input("enter id for criteria to remove from grading statistics: ")

if confirm("will remove statistics data for '" + criteriaDescription[cid] + "'"):
	for s in students:
		for key in s.adjustmentsByAssignment:
			if cid in s.adjustmentsByAssignment[key]:
				s.adjustmentsByAssignment[key].pop(cid)

if confirm("Save the student data? "):
	utilities.dataToSave['students']=True
	finish(True)