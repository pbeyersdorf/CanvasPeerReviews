#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
# if no assignments have yet been graded then prompt for graders
print("Not assigning any graders.  If your class uses graders edit this script to uncomment the code block below this message")
# if len([g for g in graded_assignments.values() if g.graded])==0: 
# 	assignGraders()
# else:
# 	viewGraders()
# 	val=inputWithTimeout("(g) update grader list",3)
# 	if (val=='g'):
# 		assignGraders()
activeAssignment=utilities.nearestAssignment

# Get creations and reviews

if not confirm("Assign peer reviews for " + activeAssignment.name + "? "):
	activeAssignment=chooseAssignment(requireConfirmation=False)
#params=getParameters(selectedAssignment=activeAssignment) # uncomment this to force an update of the parameters for this assignment
getStudentWork(activeAssignment, includeReviews=True)
assignCalibrationReviews(assignment=activeAssignment)
	
if not confirm("Calibration reviews assigned.  Continue?"):
	finish()
	exit()
	
# Assign remaining reviews  
assignPeerReviews(creations, numberOfReviewers=params.numberOfReviews, AssignPeerReviewsToGraderSubmissions=False)

if not params.combineSubmissionAndReviewGrades:
	reviewScoreAssignment=createRelatedAssignment(activeAssignment)	

webbrowser.open(activeAssignment.html_url + "/peer_reviews")	 
if not confirm("The peer review assignment have been opened in a web browser.  Verify they look correct."):
	undoAssignedPeerReviews()
	finish()
	exit()

sendSeparateMessageToEachSection=False
if sendSeparateMessageToEachSection:
	for sectionName in sorted(list(sections.values())):
		url=getSolutionURLs(assignment=activeAssignment, fileName="solution urls for " + sectionName + ".csv")
		if (url==""):
			url=confirm("Enter the URL for the solutions for '"+activeAssignment.name+"' for " + sectionName +": ", True)
		webbrowser.open(url)
		while not confirm("Verify the correct solutions for " + sectionName + " opened in a web browser. "):
			url=input("Enter the URL for the solutions for '"+activeAssignment.name+"' for " + sectionName +": ").strip()
		# Post announcement telling students the peer reviews have been assigned
		subject=("Peer reviews and solutions for " + activeAssignment.name)
		activeAssignment.solutionsUrl = url
		body=processTemplate(None,activeAssignment,"message about posted solutions")
		print(subject +"\n"+body+"\n\n")
		body=confirmText(body, prompt="Is this announcement acceptable?")
		#if confirm("Send announcement to "+ sectionName +"?", False):
		print("Sending announcement to "+ sectionName)
		key=[k for k in sections if sections[k]==sectionName][0] #get the sectionID
		announce(subject, body, key)
else:
	url=getSolutionURLs(assignment=activeAssignment)
	if (url==""):
		url=input(f"Enter the URL for the solutions for '{activeAssignment.name}': ").strip()
	webbrowser.open(url)
	while not confirm("Verify the correct solutions opened in a web browser. "):
		url=input(f"Enter the URL for the solutions for '{activeAssignment.name}': ").strip()
		webbrowser.open(url)
	# Post announcement telling students the peer reviews have been assigned
	subject=f"Peer reviews and solutions for {activeAssignment.name}"
	activeAssignment.solutionsUrl = url
	body=processTemplate(None,activeAssignment,"message about posted solutions")
	print(f"{subject}\n{body}\n\n")
	body=confirmText(body, prompt="Is this announcement acceptable - it wil be sent to the entire class?")
	print("Sending announcement" )
	announce(subject, body)
	

finish(True)
# if confirm("If you assigned or deleted any peer reviews manually, the data needs to be resyncronized.  Shall we resynchonize?"):
# 	resyncReviews(activeAssignment, creations)
# 	utilities.dataToSave['students']=True
# finish(True)
