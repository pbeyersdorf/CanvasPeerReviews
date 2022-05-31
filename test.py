from CanvasPeerReviews import *

#################  course info  #################
COURSE_ID=1324968 # Phys 50 Fall 2019 
COURSE_ID=1366437 # new Phys 220e class

CANVAS_URL = "https://sjsu.instructure.com"
TOKEN = "12~81aMfKnknlt6LUZLBbdFI60l85D2DslWoLBONS11jgIAXE8AWAhBUFG2gPDK4LN8"

canvas = Canvas(CANVAS_URL, TOKEN)
course = canvas.get_course(COURSE_ID)

students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID)

assignment=lastAssignment
creations=[]
for i,assignment in graded_assignments.items():
	submissions=assignment.get_submissions()
	for submission in submissions:
		try:
			submission.courseid=assignment.courseid
			submission.reviewCount=0
			submission.author=studentsById[submission.user_id]
			creations.append(Creation(submission))			
		except:
			status['err']="key error"

rubrics=course.get_rubrics()
rubricNum=-1
ids={}
creationids={}
outcomeids={}
rubricsById={}
for rubric in rubrics:
	rubricNum+=1
	rubric=course.get_rubric(rubric.id,include='assessments', style='full')
	if hasattr(rubric, 'assessments'):
		print("considering new rubric #", rubricNum)
		for creation in creations:
			for assessment in rubric.assessments:
				if ((assessment['assessment_type']=='grading' or assessment['assessment_type']=='peer_review') and creation.id == assessment['artifact_id'] ):
					data=assessment['data']
					rubricsById[rubric_id]=True
					reviewer_id = assessment['assessor_id']
					review_type = assessment['assessment_type']
					for s in data:
						s['description']=''
						if s['id']=='_5851':
							print(s)
							break
						if s['id'] in ids:
							ids[s['id']]=ids[s['id']]+1
						else:
							ids[s['id']]=0
						if s['criterion_id'] in creationids:
							creationids[s['criterion_id']]=creationids[s['criterion_id']]+1
						else:
							creationids[s['criterion_id']]=0
						if s['learning_outcome_id'] in outcomeids:
							outcomeids[s['learning_outcome_id']]=outcomeids[s['learning_outcome_id']]+1
						else:
							outcomeids[s['learning_outcome_id']]=0
ids
creationids					
outcomeids

students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID)

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
getStudentWork()
calibrate()
grade(lastAssignment)
exportGrades(lastAssignment, display=True)
