import sys, os
from cpr import *

students, graded_assignments, lastAssignment = initialize()

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
getStudentWork()
calibrate()
#overrideDefaultPoints(lastAssignment)
grade(lastAssignment)
exportGrades(lastAssignment, display=True)
