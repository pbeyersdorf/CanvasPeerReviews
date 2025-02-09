#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

ga=assignmentByNumber[11]
getStudentWork(ga)
studentsWithSuspectReviews=[]
cid1=[key for key in criteriaDescription if criteriaDescription[key]=='Physics concepts'][0]
cid2=[key for key in criteriaDescription if criteriaDescription[key]=='Other'][0]

for s in students:
	for key,review in s.reviewsGiven.items():
		if review.assignment_id == ga.id:
			try:
				if review.scores[cid1] != review.scores[cid2]:
					if s not in studentsWithSuspectReviews:
						studentsWithSuspectReviews.append(s)
						
					print(s.name, "("+str(s.id)+") review of " , studentsById[review.author_id].name ,review.scores[cid1] - review.scores[cid2] )
			except:
				pass
print(f"The following students gave reviews where the '{criteriaDescription[cid1]}' score did not match the '{criteriaDescription[cid2]}' score")	
for s in studentsWithSuspectReviews:
	print("\t"+s.name)
print([s.id for s in studentsWithSuspectReviews])
print("to change their scores that will be posted use a line of the form:")
print("student.points[assignment.id]['curvedTotal']=x")
print("to add a comment use a line of the form")
print("student.comments[assignment.id]+='xxx'")

