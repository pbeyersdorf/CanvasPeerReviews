from credentials import *
import sys, os
sys.path.insert(0, "/Volumes/T7/peteman/Documents/GitHub/CanvasPeerReviews")
sys.path.insert(0, "/Users/peteman/Documents/GitHub/CanvasPeerReviews")
from CanvasPeerReviews import *

#################  course info  #################
canvas = Canvas(CANVAS_URL, TOKEN)
course = canvas.get_course(COURSE_ID)
DATADIRECTORY=os.path.dirname(os.path.realpath(__file__)) + "/Data/"
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
#params=getParameters()
#assignGraders()

# Get creations and reviews
getStudentWork()
activeAssignment=lastAssignment

currentCreations=[c for c in creations if c.assignment_id == activeAssignment.id]

countAssignedReviews(currentCreations)
assignedAssessmentsToStudents=0
assignedAssessmentsToGraders=0
for student in students:
	try:
		if student.role == 'student':
			assignedAssessmentsToStudents+=student.reviewCount[activeAssignment.id]
		else:
			assignedAssessmentsToGraders+=student.reviewCount[activeAssignment.id]
	except:
		print("error getting review count for " +student.name)
assignedAssessments=assignedAssessmentsToGraders+assignedAssessmentsToStudents	
		
completedAssessmentsByGraders=0
completedAssessmentsByStudents=0
completedAssessmentsByInstructor=0
rubrics=course.get_rubrics()
graderIDs=[s.id for s in students if s.role=='grader']
for rubric in rubrics:
	rubric=course.get_rubric(rubric.id,include='assessments', style='full')
	if hasattr(rubric, 'assessments'):
		for creation in currentCreations:
			for assessment in rubric.assessments:
				if (assessment['assessment_type']=='grading' and creation.id == assessment['artifact_id'] ):
					completedAssessmentsByInstructor+=1
				if ( assessment['assessment_type']=='peer_review' and creation.id == assessment['artifact_id'] ):
					if assessment['assessor_id'] in graderIDs:
						completedAssessmentsByGraders+=1
					else:
						completedAssessmentsByStudents+=1
completedAssessments=completedAssessmentsByGraders+completedAssessmentsByStudents
checkForUnreviewed(activeAssignment)
print("")
print(str(completedAssessmentsByInstructor) + " assignments graded by instructor")
print(str(int(100*completedAssessmentsByStudents/assignedAssessmentsToStudents)) + "% of assessments by students been completed")
print(str(int(100*completedAssessmentsByGraders/assignedAssessmentsToGraders)) + "% of assessments by graders been completed")
#print(str(int(100*completedAssessments/assignedAssessments)) + "% of total assessments have been completed")


delinquentReviewers=[s for s in students if s.role=='student' and s.numberOfReviewsGivenOnAssignment(activeAssignment.id)==0]
delinquentReviewerAddresses=[str(s.id) for s in students if s.role=='student' and s.numberOfReviewsGivenOnAssignment(activeAssignment.id)==0 and s.id!=4508048]
print("No reviews by", len(delinquentReviewers),"students:")
for student in delinquentReviewers:
	print("\t" + student.name)
msg="I noticed you haven't yet completed any of your assigned peer reivews.  Remember that these are due before our next class and count for 30% of your grade on the quiz.  Here are instructions on how to submit a peer review: \nhttps://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-a-peer-review-to-an-assignment/ta-p/293"
if confirm("Shall I message these students to remind them?"):
	for address in delinquentReviewerAddresses:
		canvas.create_conversation(recipients=address, body=msg, subject='Reminder to complete your peer reviews')
		print("messaging " +  studentsById[int(address)].name)
	print("done!")
else:
	print("OK, no messages sent")