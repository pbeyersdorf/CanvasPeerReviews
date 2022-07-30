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
assignGraders()

# Get creations and reviews
getStudentWork()

if (lastAssignment.countPeerReviews()==0):
	print("Time to assign peer reviews for ", lastAssignment.name) 		
	assignCalibrationReviews()		
		
	# Assign remaining reviews  
	assignPeerReviews(creations, numberOfReviewers=params.numberOfReviews)	
	input("Open the assignment at " + lastAssignment.html_url + "/peer_reviews to verify the peer reivews have been assigned properly.  Hit <enter> to continue")

	if not getSolutionURLs():
		solutionURLs[lastAssignment.id]=confirm("Enter the URL for the solutions for '"+lastAssignment.name+"': ", True)

	# Post announcement telling students the peer reviews have been assigned
	subject=("Peer reviews and solutions for " + lastAssignment.name)
	body=("Peer reviews have been assigned and <a href='"+solutionURLs[lastAssignment.id]+"'>solutions to " +lastAssignment.name+ "</a> have been posted.  Please " +
		" review the solutions and then do your peer reviews.")
	print(subject +"\n"+body+"\n\n")
	if confirm("Send announcement?", False):
		announce(subject, body)
	
elif peerReviewingOver(lastAssignment):
	print("Lets look for any regrades from the previous week")
	regrade()
	print("Peer reviews period is over ... let's assign grades") 
	calibrate()
	grade(lastAssignment)				
	print("\nGrades save to file 'scores for " + lastAssignment.name + "'")
	exportGrades(lastAssignment, display=True)
	if confirm("Post grades on canvas?", False):
		postGrades(lastAssignment)
	print("\nGrading Power Rankings")
	gradingPowerRanking()
	print("\nGrading Deviation Rankings")
	gradingDeviationRanking()

print("Done!")