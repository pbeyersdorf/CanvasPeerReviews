#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
print("Running calincalibrate and grade for assignment 5 as a test")


ga=assignmentByNumber[5]
getStudentWork(ga)
#cs=[c for c in creations if c.author_id in studentsById] # don't consider any submission by students we don't know about
#resyncReviews(ga,cs)
calibrate(endDate=ga.date)
grade(ga)

s=students[0]
cid='_2681'
print(f"Looking just at {s.name} on {ga.name} for {criteriaDescription[cid]}:")
print(f"Adjustment object has an rms of {s.adjustmentsByAssignment[ga.id][cid].rms}")
print(f"rmsByAssignment has recorded an rms of {s.rmsByAssignment[ga.id][cid]}")