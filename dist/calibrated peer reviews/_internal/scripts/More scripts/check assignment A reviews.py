#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

ga=chooseAssignment()
getStudentWork(ga)
studentsWithSuspectReviews=[]
for s in students:
	for key,review in s.reviewsGiven.items():
		if review.assignment_id == ga.id:
			try:				
				if review.scores['_4049'] != 4.5:
					if s not in studentsWithSuspectReviews:
						studentsWithSuspectReviews.append(s)
						
					print(s.name, "("+str(s.id)+") review of " , studentsById[review.author_id].name ,review.scores['_4049'] - review.scores['_5705'] )
			except:
				pass
print("The following students gave reviews where the 'other' score did not match the '4.5' required")	
for s in studentsWithSuspectReviews:
	print("\t"+s.name)
print([s.id for s in studentsWithSuspectReviews])
print("to change their scores that will be posted use a line of the form:")
print("student.points[assignment.id]['curvedTotal']=x")
print("to add a comment use a line of the form")
print("student.comments[assignment.id]+='xxx'")

msg="When looking over the peer reviews you gave last week on the practice review assignment where people drew a self-portrait I noticed that you did not award the points as you were asked to in the instructions (you were told to award scores of 5/4/4/4.5).  This purpose of this assignment was for me to catch and correct these sort of issues before we start peer reviews on quizzes.  Although you got full creedit for the practice assignment, in order to receive full credit on the quizzes you will need to carefully follow the review instructions.  As a reminder the review instructions (or a link to them) will be sent in a canvas announcement shortly after the quiz.  Make sure to thouroughly read the instructions before doing any peer reviews.  Let me know if you have any questions."
print(msg)
if confirm("send message to students?"):
	message(studentsWithSuspectReviews, msg)
