from CanvasPeerReviews import *
import os

#################  course info  #################
COURSE_ID = 1234567 
CANVAS_URL = "https://sjsu.test.instructure.com"
TOKEN = "PUT_YOUR_TOKEN_HERE"
DATADIRECTORY=os.path.dirname(os.path.realpath(__file__)) + "/Data/"
#students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
students, graded_assignments, lastAssignment = initialize()

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
#getStudentWork()
regrade()
print("Done!")