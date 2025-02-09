#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

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

#Choose what section to work on
secByNum=dict()
for sectionName in sorted(list(sections.values())):
	secNum=int(sectionName[-1:])
	secByNum[secNum]=sectionName
	print (secNum, secByNum[secNum])
sectionName=secByNum[getNum("Choose a section: ")]
while not confirm(sectionName):
	sectionName=secByNum[getNum("Choose a section: ")]

if confirm("reassign students and graders for different sections final exams?"):
	#reassign these graders for this section
	s=selectStudentByName("Harold") # can only grade section 3
	s.section=1839966
	s.sectionName='FA22: PHYS-51 Section 03'
	print(f"Assigning {s.name} to {s.sectionName}")

	#reassign these graders for this section
	s=selectStudentByName("Nikitha") # can grade sections 3, update this after the first final
	s.section=1839966
	s.sectionName='FA22: PHYS-51 Section 03'
	print(f"Assigning {s.name} to {s.sectionName}")

	#reassign Jason Nguyen to take the exam with section 5
	s=selectStudentByName("Jason Nguyen")
	s.section=1839970
	s.sectionName='FA22: PHYS-51 Section 05'
	print(f"Assigning {s.name} to {s.sectionName}")

	s=selectStudentByName("Bern")
	s.section=1839970
	s.sectionName='FA22: PHYS-51 Section 05'
	print(f"Assigning {s.name} to {s.sectionName}")


finalAssignments=[graded_assignments[key] for key in graded_assignments if "Retake" in graded_assignments[key].name]

def assign(activeAssignment):
	getStudentWork(activeAssignment, includeReviews=False)
	#assign calibration review to a random student in this section
	creationsToConsider=randomize([c for c in creations if c.author_id in studentsById and studentsById[c.author_id].sectionName == sectionName and studentsById[c.author_id].role=='student'])
	if len(creationsToConsider)<2:
		print(f"Not enough submissions to assign peer reviews for {activeAssignment.name} in {sectionName}")
		log(f"Not enough submissions to assign peer reviews for {activeAssignment.name} in {sectionName}")
	else:
		studentsWithSubmissionsInThisSection=[studentsById[c.author_id] for c in creationsToConsider]
		reviewers=studentsWithSubmissionsInThisSection
		reviewers.pop(0)
		calibration=creationsToConsider[0]
		log(studentsById[calibration.author_id].name + " chosen as the calibration review for " + activeAssignment.name + " in " + sectionName)
		for j,reviewer in enumerate(reviewers):
			msg=str(j+1) + "/" + str(len(reviewers))
			peer_review=assignAndRecordPeerReview(calibration,reviewer, msg)

		#assignCalibrationReviews(calibrations="random", assignment=activeAssignment)		
		print("Calibration reviews assigned.  Now assigning remaining reviews")

		# Assign remaining reviews  
		assignPeerReviews(creationsToConsider, numberOfReviewers=params.numberOfReviews, AssignPeerReviewsToGraderSubmissions=False)
		webbrowser.open(activeAssignment.html_url + "/peer_reviews")	 
		if not confirm("The peer review assignmetn have been opened in a web browser.  Verify they look correct."):
			undoAssignedPeerReviews(assignment=activeAssignment)
		print(f"Done assigning reviews for {activeAssignment.name}.")


print("\nAssignments being considered: ")
for theActiveAssignment in finalAssignments:
	print(theActiveAssignment.name) 
if not confirm("proceed? "):
	exit()

for theActiveAssignment in finalAssignments:
	assign(theActiveAssignment)
	
dataToSave['students']=True
finish()
print("If you assigned or deleted any peer reviews manually, the data needs to be resyncronized.  Do that using 'resyncReviews(activeAssignment, creations)'")
print()
print("Send an announcement with solution urls manually, they are in the Phys51/Quiz/Final Exam folder")	