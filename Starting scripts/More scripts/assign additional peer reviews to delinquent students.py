#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
#activeAssignment=chooseAssignment(requireConfirmation=False,  timeout=5, defaultAssignment=lastAssignment)
activeAssignment=chooseAssignment(requireConfirmation=False, timeout=5, defaultAssignment=lastAssignment)
getStudentWork(activeAssignment)

# get creations that haven't yet been reviewed
unreviewedCreations=checkForUnreviewed(activeAssignment, openPage=False) #get the number of incomplete reviews
if len(unreviewedCreations)==0:
	print("No unreviewed creations to assign")
	exit()
print( len(unreviewedCreations)," unreviewed creations")

# make a list of students who havent' started their peer reviews yet
delinquentReviewers=[s for s in students if s.role=='student' and s.numberOfReviewsGivenOnAssignment(activeAssignment.id)==0 and activeAssignment.id in s.creations]
if len(delinquentReviewers) ==0 :
	print("No delinquent reviewers to assign creations to")
	exit()
print("No reviews by", len(delinquentReviewers),"students")
	
#pad the list of unreviewed creations so there is one to assign to each delinquent reviewer
while len(delinquentReviewers) > len(unreviewedCreations):
	unreviewedCreations*=2

#assign each delinquent reviewer an unreviewed creation
i=0
for reviewer, creation in zip(delinquentReviewers, unreviewedCreations):
	i+=1
	msg=f"{i}/{len(delinquentReviewers)}"
	assignAndRecordPeerReview(creation,reviewer,msg)

#confirm assignments
webbrowser.open(activeAssignment.html_url + "/peer_reviews")	 
if not confirm("The peer review assignmetn have been opened in a web browser.  Verify they look correct."):
	undoAssignedPeerReviews(assignment=activeAssignment)
utilities.dataToSave['students']=True
finish(True)
