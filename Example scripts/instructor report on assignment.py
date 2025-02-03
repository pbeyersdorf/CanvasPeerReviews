#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get course info  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
activeAssignment=chooseAssignment(requireConfirmation=False)
getStudentWork(activeAssignment)

course=utilities.course
instructors=getInstructors(course)
instructorById=dict()
calibrationsByInstructor=dict()
for instructor in instructors:
	instructorById[instructor.id]=instructor.name
	calibrationsByInstructor[instructor.name]=[]

rubrics=course.get_rubrics()
for rubric in rubrics:
	if rubric.title == graded_assignments[creations[0].assignment_id].rubric_settings['title']:
		break
rubric=course.get_rubric(rubric.id,include='assessments', style='full') #this is supposed ot be required to return the data parameter, but it sometimes times out
try:
	for creation in creations:
		for assessment in rubric.assessments:
			if (assessment['assessment_type']=='grading' and creation.id == assessment['artifact_id'] ):
				assessment['assessor_id']
				instructorName=instructorById[assessment['assessor_id']]
				print(instructorName + " reviewed " + studentsById[creation.user_id].name)
				calibrationsByInstructor[instructorName].append(studentsById[creation.user_id].name)
except:
	print(f"Unable to get {rubric.title} for this assignment.  Skipping...")
	
for instructor in calibrationsByInstructor:
	print(f"{instructor} graded {len(calibrationsByInstructor[instructor])} reports")	
	print("    " + ", ".join(calibrationsByInstructor[instructor]))
