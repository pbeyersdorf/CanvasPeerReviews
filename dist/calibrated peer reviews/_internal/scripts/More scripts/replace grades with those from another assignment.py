#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

# get the assignments
approved=False
while not approved:
	print("This script will take grades from a 'source' assignment and copy them to a 'target' assignment if they are higher than the student's orignal grade in the target assignment.")
	targetAssignment=chooseAssignment(requireConfirmation=False, prompt="Choose a target assignment:")
	sourceAssignment=chooseAssignment(requireConfirmation=False, prompt="Choose a source assignment: ")
	approved=confirm(f"Will copy grades from '{sourceAssignment.name}' to '{targetAssignment.name}' if it is a higher score")

#update the target scores in the database using data posted on Canvas
submissions=targetAssignment.get_submissions()
for creation in submissions:
	creation.author_id=creation.user_id
	if creation.author_id in studentsById:
		if creation.score !=None:
			studentsById[creation.author_id].grades[targetAssignment.id]['curvedTotal']=creation.score


#sort out the students
studentsToChange=[s for s in students if sourceAssignment.id in s.grades and s.grades[sourceAssignment.id]['curvedTotal'] > s.grades[targetAssignment.id]['curvedTotal']]
studentsToNotChange=[s for s in students if sourceAssignment.id in s.grades and not s.grades[sourceAssignment.id]['curvedTotal'] > s.grades[targetAssignment.id]['curvedTotal']]
	
#process the students
postCommentsForUnchangedScore=confirm("Should we post comments on " + targetAssignment.name + "for students whose score was not improved?")
postWithoutConfirmation=not confirm("Do you want to confirm each grade before it is uploaded? ")

def post(theSubmission, comment, score=None):
	print("Posting is disabled but would have posted: [" + str(score) +"] " + comment)
	if score != None:
		theSubmission.edit(submission={'posted_grade':score})
	theSubmission.edit(comment={'text_comment':comment})
	print("Posting: [" + str(score) +"] " + comment)


studentsWithoutASubmission=[]
for student in students:
	try:
		creation=student.creations[targetAssignment.id]
		if student in studentsToChange and (postWithoutConfirmation or confirm(f"Will replace score of {creation.score} with {newScore} for {student.name}: ")):
			post(creation, "Your score for this assignment has been replaced with the score from " + sourceAssignment.name, score=student.grades[sourceAssignment.id]['curvedTotal'])
		if student in studentsToNotChange and postCommentsForUnchangedScore:
			post(creation, "Your score for this assignment has been replaced with the score from " + sourceAssignment.name)
	except:
		studentsWithoutASubmission.append(student)
#process the students who weren't able to be processed initially.  This method is slower but more reliable
ta=[a for a in utilities.assignments if a.id==targetAssignment.id][0]
unprocessedStudents=[]
for student in studentsWithoutASubmission:
	try:
		submission=ta.get_submission(student.id)
		if student in studentsToChange and (postWithoutConfirmation or confirm(f"Will replace score of {creation.score} with {newScore} for {student.name}: ")):
			post(submission, "Your score for this assignment has been replaced with the score from " + sourceAssignment.name, score=student.grades[sourceAssignment.id]['curvedTotal'])
		if student in studentsToNotChange and postCommentsForUnchangedScore:
			post(submission, "Your score for this assignment has been replaced with the score from " + sourceAssignment.name)		
	except:
		unprocessedStudents.append(student)
for student in unprocessedStudents:
	print("Unable to process " + student.name + " please process manually")
	#utilities.assignments

log("Grades updated for " +targetAssignment.name+ " using scores from " + sourceAssignment.name)
