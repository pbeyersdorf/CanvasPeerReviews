#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from CanvasPeerReviews import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
# if no assignments have yet been graded then prompt for graders
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
getStudentWork(activeAssignment, includeReviews=True)
#assignCalibrationReviews(assignment=activeAssignment)

#Choose what section to work on
secByNum=dict()
calibrationMessages=[]
classInstructors=[user.name for user in course.get_users(enrollment_type=['Teacher'])]
for sectionName in sorted(list(sections.values())):
	secNum=int(sectionName[-1:])
	secByNum[secNum]=sectionName
	print (f"Working on section {secNum}: {sectionName}")

	#assign calibration review to a random student in this section
	creationsToConsider=randomize([c for c in creations if c.author_id in studentsById and studentsById[c.author_id].sectionName == sectionName and studentsById[c.author_id].role=='student'])
	if len(creationsToConsider)<2:
		print(f"Not enough submissions to assign peer reviews for {activeAssignment.name} in {sectionName}")
		log(f"Not enough submissions to assign peer reviews for {activeAssignment.name} in {sectionName}")
	else:
		calibrations=assignCalibrationReviews(calibrations="auto", assignment=activeAssignment)
		message=f'{" ,".join([studentsById[calibration.author_id].name for calibration in calibrations])} work has been assigned as calibrations for section {secNum}'
		calibrationMessages.append(message)
		log(message, display=True)
		print("Now assigning remaining reviews")
		# Assign remaining reviews  
		assignPeerReviews(creationsToConsider, numberOfReviewers=params.numberOfReviews, AssignPeerReviewsToGraderSubmissions=False)
		webbrowser.open(activeAssignment.html_url + "/peer_reviews")	 
		if not confirm("The peer review assignmetn have been opened in a web browser.  Verify they look correct."):
			undoAssignedPeerReviews(assignment=activeAssignment)
		print(f"Done assigning reviews for {activeAssignment.name}.")

		sectionInstructors=[enr.user for enr in sec.get_enrollments() if enr.user['name'] in classInstructors]
		for instructor in sectionInstructors:
			if confirm(f"Send a message to {instructor['name']} about the calibration review?")
			message+="\nPlease make sure to review this submission."
			utilities.canvas.create_conversation(instructor['id'], body=message, subject="calibration review")

	url=getSolutionURLs(assignment=activeAssignment, fileName="solution urls for " + sectionName + ".csv")
	if (url==""):
		url=confirm("Enter the URL for the solutions for '"+activeAssignment.name+"' for " + sectionName +": ", True)
	webbrowser.open(url)
	while not confirm("Verify the correct solutions for " + sectionName + " opened in a web browser. "):
		url=input("Enter the URL for the solutions for '"+activeAssignment.name+"' for " + sectionName +": ").strip()
	# Post announcement telling students the peer reviews have been assigned
	subject=("Peer reviews and solutions for " + activeAssignment.name)
	activeAssignment.solutionsUrl = url
	body=processTemplate(student=None,assignment=activeAssignment,name="message about posted solutions")
	print(subject +"\n"+body+"\n\n")
	body=confirmText(body, prompt="Is this announcement acceptable?")
	#if confirm("Send announcement to "+ sectionName +"?", False):
	print("Sending announcement to "+ sectionName)
	key=[k for k in sections if sections[k]==sectionName][0] #get the sectionID
	announce(subject, body, key)
	

if confirm("If you assigned or deleted any peer reviews manually, the data needs to be resyncronized.  Shall we resynchonize?"):
	resyncReviews(activeAssignment, creations)
	utilities.dataToSave['students']=True

print("\n".join(calibrationMessages))
	
dataToSave['students']=True
finish()
print("If you assigned or deleted any peer reviews manually, the data needs to be resyncronized.  Do that using 'resyncReviews(activeAssignment, creations)'")
print()
print("Send an announcement with solution urls manually, they are in the Phys51/Quiz/Final Exam folder")	