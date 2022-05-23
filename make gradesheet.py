from CanvasPeerReviews import *
import os

#################  course info  #################
COURSE_ID = 1477183 
CANVAS_URL = "https://sjsu.instructure.com"
TOKEN = "PUT_YOUR_TOKEN_HERE"
DATADIRECTORY=os.path.dirname(os.path.realpath(__file__)) + "/Data/"
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

fileName=DATADIRECTORY + "gradesheet.csv"
exportGrades(fileName=fileName)
if confirm("Edit the grades in the Data folder, and then click OK.  You will be prompted for an assignment to post them to (this part is untested)."):
	postFromCSV(fileName)
print("Done!")