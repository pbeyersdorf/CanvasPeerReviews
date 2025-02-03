#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
activeAssignment=chooseAssignment(requireConfirmation=False)
getStudentWork(activeAssignment)

print("There are " + str(len(creations)) + " creations on " + activeAssignment.name)
val=inputWithTimeout("(v) view list of assigned reviews?")
count=0
if val=="v":
	for creation in creations:
		for peer_review in creation.get_submission_peer_reviews():
			count+=1
			reviewer=studentsById[peer_review.assessor_id]
			#print(str(count) +") "+reviewer.name + " assignment of "  + studentsById[creation.author_id].name +"'s work")
			#print("{: >25} reviews {: <30}{: <4}".format(reviewer.name,studentsById[creation.author_id].name, str(count)))
			printLeftRight("{: >25} reviews {: <30}".format(reviewer.name,studentsById[creation.author_id].name),str(count))
total=count

val=""
val2=""
count=0

onlyShowIncompletes=confirm("Should we only look at reviews that have yet to be completed?")

for creation in creations:
	for peer_review in creation.get_submission_peer_reviews():
		reviewer=studentsById[peer_review.assessor_id]
		count+=1
		if peer_review.workflow_state!='completed':
			if val != 'D':
				print(str(count) + ") " + reviewer.name + " assignment of "  + studentsById[creation.author_id].name +"'s work")
				val=input('(d) to delete this one, (D) to delete all for this <enter> to skip: ').strip()
			if val.lower()=='d':
				deleteReview(peer_review)
		else:
			if val2!="DELETE" and val2!="SKIP" and not onlyShowIncompletes:
				print(str(count) + ") " + Fore.RED + reviewer.name + " assignment of "  + studentsById[creation.author_id].name +"'s work was already completed" + Style.RESET_ALL)
				val2=input("type 'delete' to force a deletion, 'DELETE' to delete all complete, 'SKIP' to skip all complete or <enter> to skip this one: ").strip()
			if val2.lower()=='delete':
				deleteReview(peer_review)
		