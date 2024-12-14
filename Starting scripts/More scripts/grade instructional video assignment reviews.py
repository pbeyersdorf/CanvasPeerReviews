#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

ga=chooseAssignment()
print(f"looking at {ga.name}")
getStudentWork(ga)
theReviews=getReviews(creations)

studentsWithSuspectReviews=[]
studentsReceivingZeros=[]
studentsCreationScores=[]
studentsReviewScores=[]
for s in students:
	reviewsByStudent=[r for r in theReviews if r.reviewer_id == s.id]
	reviewsOfStudents=[r for r in theReviews if r.author_id == s.id]
	total=0
	try:
		for r in reviewsByStudent:
			total+=r.data[0]['points']
		if len(reviewsByStudent)>0:
			avg=total/len(reviewsByStudent)
			if avg==85 or avg==70:
				studentsWithSuspectReviews.append({'student': s, 'avg':avg})
				studentsReviewScores.append({'student': s, 'adj':-3, 'comment': "you lost 3 points for failling to follow the review instructions requiring you award at least one  (but not all) 'Exceptional' score"})
			else:
				studentsReviewScores.append({'student': s, 'adj':0, 'comment': ""})
		else:
			studentsReviewScores.append({'student': s, 'adj':-10, 'comment': "You lost 10 points for not completing the peer reviews"})
			
	except:
		print(s.name, "error")
		for r in reviewsByStudent:
			print(r.data)
		studentsReviewScores.append({'student': s, 'adj':0, 'comment': ""})
	total=0
	cnt=0
	for r in reviewsOfStudents:
		try:
			total+=r.data[0]['points']
			if (r.data[0]['points']==0):
				studentsReceivingZeros.append(s)
			cnt+=1
		except:
			print("error")
	if cnt>0:
		avg=total/cnt
		studentsCreationScores.append({'student': s, 'avg':int(avg)})

if len(studentsWithSuspectReviews)>0:
	print("Students who lacked diversity in the review scores they gave:")
	for data in studentsWithSuspectReviews:
		print(data['student'].name, data['avg'])

scoredStudents=[]
if len(studentsCreationScores)>0:
	print("Student Creation Scores:")
	for data in studentsCreationScores:
		s=data['student']
		adjustment=[data['adj'] for data in studentsReviewScores if data['student']==s][0]
		comment=[data['comment'] for data in studentsReviewScores if data['student']==s][0]
		points=data['avg'] + adjustment
		print(f"{s.name}, {points}, {comment}")
		s.points[ga.id]={'curvedTotal': points}
		s.comments[ga.id]=comment
		scoredStudents.append(s)

if confirm("post on canvas? "):
	postGrades(ga, listOfStudents=scoredStudents)

if confirm("Save student data? "):
	utilities.dataToSave['students']=True
	finish()
