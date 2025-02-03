import sys, os
sys.path.insert(0, "/Volumes/T7/peteman/Documents/GitHub/CanvasPeerReviews")
sys.path.insert(0, "/Users/peteman/Documents/GitHub/CanvasPeerReviews")
from cpr import *

#################  course info  #################
canvas = Canvas(CANVAS_URL, TOKEN)
course = canvas.get_course(COURSE_ID)
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID)


activeAssignment=chooseAssignment()
getStudentWork(activeAssignment)


print("This script has not yet been tested!!!")

added_points=getNum("How many points should be added to each student's score?")

if not confirm("Will add " + str(added_points) + " to all assingments"):
	print("OK...exiting without adjusting grades")
	exit()

for creation in creations:
    # Handle an unscored assignment by checking the `score` value
    if creation.score is not None:
        score = submission.score + added_points
    else:
        # Treat no submission as 0 points
        #score = 0 + added_points
		pass
		
    creation.edit(submission={'posted_grade': score})

print("OK...grades adjusted")
