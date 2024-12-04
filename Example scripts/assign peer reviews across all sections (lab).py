#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
#params=getParameters()
# if no assignments have yet been graded then prompt for graders
print("This script will assign peer reviews to students regardless of which section they are in.  Students may be asked to review someone's work from a different discussion section.")
if len([g for g in graded_assignments.values() if g.graded])==0: 
	assignGraders()
else:
	viewGraders()
	val=inputWithTimeout("(g) update grader list",3)
	if (val=='g'):
		assignGraders()

# Get creations and reviews
activeAssignment=utilities.nearestAssignment
if not confirm("Assign peer reviews for " + activeAssignment.name + "? "):
	activeAssignment=chooseAssignment(requireConfirmation=False)
params=getParameters(selectedAssignment=activeAssignment)
getStudentWork(activeAssignment, includeReviews=True)

#Choose what section to work on
secByNum=dict()
calibrationMessages=[]
classInstructors=[user.name for user in utilities.course.get_users(enrollment_type=['Teacher'])]
calibrations=assignCalibrationReviews(assignment=activeAssignment, ignoreSections=True) # will get any professor graded submission
url=""

message=f'{" ,".join([studentsById[calibration.author_id].name for calibration in calibrations])} work has been assigned as calibrations'
log(message, display=True)

creationsToConsider=randomize([c for c in creations if c.author_id in studentsById and studentsById[c.author_id].role=='student'])

print("Now assigning remaining reviews")
assignPeerReviews(creationsToConsider, numberOfReviewers=params.numberOfReviews, AssignPeerReviewsToGraderSubmissions=False, ignoreSections=True)
webbrowser.open(activeAssignment.html_url + "/peer_reviews")	 
print(f"Done assigning reviews for {activeAssignment.name}")

if not params.combineSubmissionAndReviewGrades:
		reviewScoreAssignment=createRelatedAssignment(activeAssignment)	


if (url==""):
	url=confirm("Enter the URL for the solutions for '"+activeAssignment.name+"': ", True)
	webbrowser.open(url)
	while not confirm("Verify the correct solutions opened in a web browser. "):
		url=input("Enter the URL for the solutions for '"+activeAssignment.name+"': ").strip()

# Post announcement telling students the peer reviews have been assigned
subject=("Peer reviews and solutions for " + activeAssignment.name)
activeAssignment.solutionsUrl = url
body=processTemplate(student=None,assignment=activeAssignment,name="message about posted solutions")
print(subject +"\n"+body+"\n\n")
body=confirmText(body, prompt="Is this announcement acceptable?")
print("Sending announcement")
announce(subject, body)
	

dataToSave['students']=True
finish()
print("If you assigned or deleted any peer reviews manually, the data needs to be resyncronized.  Do that using 'resyncReviews(activeAssignment, creations)'")
print()
