#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

print("\nBefore grading an assignment that you don't want included in calibrations of students grading ability set its 'includeInCalibrations' to False")

print("\nHere are the assignments that aren't included in the grader calibrations:")
uncalibratedAssignments=[graded_assignments[key] for key in graded_assignments if not graded_assignments[key].includeInCalibrations]
for ua in uncalibratedAssignments:
	print("\t" + ua.name)
cont=confirm("Do you want to add more assignments to this list??")
while cont:
	a=chooseAssignment(requireConfirmation=False, prompt="Choose an assignment to exclude from calibrations.")
	a.includeInCalibrations=False
	uncalibratedAssignments=[graded_assignments[key] for key in graded_assignments if not graded_assignments[key].includeInCalibrations]
	print("Here are the assignments that aren't included in the grader calibrations:")
	for ua in uncalibratedAssignments:
		print("\t" + ua.name)
	cont=confirm("Do you want to add more assignments to this list? ")

cont=confirm("Do you want to remove any assignments from this list? ")
while cont:
	a=chooseAssignment(requireConfirmation=False, prompt="Choose an assignment to include in calibrations.")
	a.includeInCalibrations=True
	uncalibratedAssignments=[graded_assignments[key] for key in graded_assignments if not graded_assignments[key].includeInCalibrations]
	print("Here are the assignments that aren't included in the grader calibrations:")
	for ua in uncalibratedAssignments:
		print("\t" + ua.name)
	cont=confirm("Do you want to add more assignments to this list? ")
	
utilities.dataToSave['assignments']=True



askToSaveStudents=False
theKeys=[]
for s in students:
	theKeys=theKeys+list(s._dataByAssignment.keys())
theKeys=list(set(theKeys))
assignmetnsToRemoveDeviationDataFrom=[ua for ua in uncalibratedAssignments if ua.id in theKeys]
if len(assignmetnsToRemoveDeviationDataFrom)>0:
	print("\nThe following assignments already have student calibration data")
	for a in assignmetnsToRemoveDeviationDataFrom:
		print("\t" + a.name)
	if confirm("Delte this data? "):
		for a in assignmetnsToRemoveDeviationDataFrom:
			for s in students:
				try:
					s._dataByAssignment.pop(a.id)
					print(f"Deleting {s.name}'s data for {a.name}", end="\r")
				except:
					pass
		askToSaveStudents=True
		
theKeys=[]
for s in students:
	theKeys=theKeys+list(s._dataByAssignment.keys())
theKeys=list(set(theKeys))
assignmetnsToAddDeviationDataFrom=[graded_assignments[key] for key in graded_assignments if graded_assignments[key].includeInCalibrations and key not in theKeys and graded_assignments[key].graded]
if len(assignmetnsToAddDeviationDataFrom)>0:
	print("\nThe following assignments don't have student calibration data")
	for a in assignmetnsToAddDeviationDataFrom:
		print("\t" + a.name)
	if confirm("Add this data? "):
		for a in assignmetnsToAddDeviationDataFrom:
			getStudentWork(a)
			cs=[c for c in creations if c.authod_id in studentsById] # don't consider any submission by students we don't know about
			resyncReviews(a,cs)
		askToSaveStudents=True

if askToSaveStudents and confirm("Save student data? "):
	utilities.dataToSave['students']=True
finish()
exit()