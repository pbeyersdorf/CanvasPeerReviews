#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

ga=assignmentByNumber[15]
getStudentWork(ga)
studentsWithSuspectReviews=[]

for s in students:
	for key,review in s.reviewsGiven.items():
		if review.assignment_id == ga.id:
			try:
				if review.scores['_2681'] != review.scores['_4049']:
					if s not in studentsWithSuspectReviews:
						studentsWithSuspectReviews.append(s)
					print(s.name, "(" + str(s.id) +")", "review of " , studentsById[review.author_id].name ,review.scores['_4049'] - review.scores['_2681'] )
			except:
				pass
print("The following students gave reviews where the 'other' score did not match the 'Physics Concepts' score")	
for s in studentsWithSuspectReviews:
	print("\t"+s.name)
print([s.id for s in studentsWithSuspectReviews])
print("to change their scores that will be posted use a line of the form:")
print("student.points[assignment.id]['curvedTotal']=x")
print("to add a comment use a line of the form")
print("student.comments[assignment.id]+='xxx'")
