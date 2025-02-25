#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
activeAssignment=chooseAssignment(requireConfirmation=False)
success=False
tries=0
while not success and tries<10:
	try:
		tries+=1
		getStudentWork(activeAssignment)
		success=True
	except:
		print(f"{tries}/10: Errror getting student work.  Trying again as this may fix the problem…")
if tries==10:
	print("I tried and failed 10 times.  Even Sisyphus wouldn't want to continue so I'm giving up.")
	exit()
val=input("Enter a student's name whose reviews should be reset: ")
while val != "":
	reviewer=selectStudentByName(val)
	success=False
	#first try the fast way using reviews saved in the student object
	reviewsGivenByThisStudentOnThisAssignment=[reviewer.reviewsGiven[key] for key in reviewer.reviewsGiven if reviewer.reviewsGiven[key].assignment_id==activeAssignment.id]

	msg0="Hi "+reviewer.name.split(" ")[0]+",  Your assigned peer reviews have been deleted and reassigned.  "
	msg1="For your reference here is what you had entered initially:\n\n"
	for review in reviewsGivenByThisStudentOnThisAssignment:
		peer_review=review.peer_review
		creation=[c for c in creations if c.id==peer_review.asset_id][0]
		msg1+=f"for '{review.creation.attachments[0].filename}':"
		msg1+=reviewSummary(review)
		deleteReview(peer_review)
		peer_review=assignAndRecordPeerReview(creation,reviewer, "")
		success=True
		msg1+="\n"
	#if that doesn't work, probe canvas to find the assigned reviews
	if not success:
		for creation in creations:
			for peer_review in creation.get_submission_peer_reviews():
				reviewer=studentsById[peer_review.assessor_id]
				if reviewer==reviewer:
					deleteReview(peer_review)
					peer_review=assignAndRecordPeerReview(creation,reviewer, "")

		msg=confirmText(msg0)
	else:
		msg=confirmText(msg0+msg1)
	log("reset review [" + review.fingerprint() + "]")
	if confirm("Send message? "):
		message(reviewer, body=msg, subject='reassigned peer review', display=False)
	val=input("Enter another student's name whose reviews should be reset, or <enter> when done: ")

# this shouldn't be necessary since the studentr data gets updated when I delete or add a new peer review
# resyncReviews(activeAssignment,creations)

utilities.dataToSave['students']=True
finish(True)