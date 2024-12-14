#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

importedAssignmentName=[]
overwrite=confirm("Do you want to overwrite existing grades in the python database (this will not affect grades posted on canvas, if you say no only grades that don't exist in the database will be imported)?")
for key in graded_assignments:
	activeAssignment=graded_assignments[key]
	try:
		importGrades(activeAssignment, overwrite=overwrite)
		importedAssignmentName.append(activeAssignment.name)
	except Exception as err:
		print(err)

if confirm("Imported grades for " + "\n\t".join(importedAssignmentName) + "\nShall we save the data? "):
	utilities.dataToSave['students']=True
	finish(True)

	