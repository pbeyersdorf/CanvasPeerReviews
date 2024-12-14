#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
#activeAssignment=chooseAssignment(requireConfirmation=False,  timeout=5, defaultAssignment=lastAssignment)
activeAssignment=lastAssignment
getStudentWork(activeAssignment)

while True:
	val=input("\nWho is the reviewer who needs a review reset?\nEnter a partial name or <ctrl-c> to end: ")
	reviewer=selectStudentByName(val)
	reviewFileName=input("Enter partial filename for review: ")

	possibleMatches=[]
	reviewsGivenByThisStudentOnThisAssignment=[reviewer.reviewsGiven[key] for key in reviewer.reviewsGiven if reviewer.reviewsGiven[key].assignment_id==activeAssignment.id]
	for review in reviewsGivenByThisStudentOnThisAssignment:
		ce=review.creation.edit()
		for sub in ce.all_submissions:
			for a in sub['attachments']:
				if reviewFileName in a['filename']:
					possibleMatches.append(review)
				
	if len(possibleMatches)==0:
		print("No matching peer review found")
	else:
		if len(possibleMatches)>1:
			print(f"{len(possibleMatches)} submissions found that could be a match.")
			for pr in possibleMatches:
				print(f"\treview of {studentsById[pr.author_id].name}")
			print("Please be more specific if you only want to reset only one.")
			proceed=confirm("\nReset all matches? ")
		else:
			proceed=True
		if proceed and findInLog(review.fingerprint()):
			proceed=confirm("This review had previously been reset.  Reset again?")
		if proceed: 
			for review in possibleMatches:
				peer_review=review.peer_review
				creation=review.creation
				if findInLog(review.fingerprint()):
					proceed=confirm("This review had previously been reset.  Reset again?")
				else:
					proceed=True
				if proceed:
					authorName=studentsById[review.author_id].name
					print("Found review of " + authorName +" by " + reviewer.name)
					if confirm("reset review?" ):
						msg1="Hi "+reviewer.name.split(" ")[0]+",  One of your peer reviews had an issue and since it can't be reset I have deleted it and reassigned it so you can resubmit it.  For your reference here is what you had entered initially:\n\n"
						msg1+=reviewSummary(review)
						msg=confirmText(msg1)
						deleteReview(peer_review)
						assignAndRecordPeerReview(creation,reviewer, "")
						log("reset review [" + review.fingerprint() + "]")
						message(reviewer, body=msg, subject='reassigned peer review', display=False)
						print("Resyncing review info")
						#allowPrinting(False)
						#resyncReviews(activeAssignment,creation)
						#allowPrinting(True)	
