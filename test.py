from CanvasPeerReviews import *

#################  course info  #################
COURSE_ID=1324968 # Phys 50 Fall 2019 
#COURSE_ID=1366437 # new Phys 220e class

CANVAS_URL = "https://sjsu.test.instructure.com"
TOKEN = "12~81aMfKnknlt6LUZLBbdFI60l85D2DslWoLBONS11jgIAXE8AWAhBUFG2gPDK4LN8"

canvas = Canvas(CANVAS_URL, TOKEN)
course = canvas.get_course(COURSE_ID)

students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID)

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
getStudentWork()
calibrate()
regrade()
grade(lastAssignment)
exportGrades(lastAssignment, display=True)
