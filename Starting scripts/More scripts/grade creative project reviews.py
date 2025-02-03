#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

ga=chooseAssignment()
print(f"looking at {ga.name}")
getStudentWork(ga)
theReviews=getReviews(creations)

#fix points assigned
total=0
cnt=0
for r in theReviews:
	if r.data[0]['points']==4:
		r.data[0]['points']=100
	elif r.data[0]['points']==3:
		r.data[0]['points']=90
	elif r.data[0]['points']==2.4 or r.data[0]['points']==2:
		r.data[0]['points']=80
	elif r.data[0]['points']==0.8 or r.data[0]['points']==1 :
		r.data[0]['points']=70
	total+=r.data[0]['points']
	cnt+=1


studentsCreationScores=[]
studentsReviewScores=[]
print("Requiring each reviewer assign at at least 3 unique grades")
for s in students:
	reviewsByStudent=[r for r in theReviews if r.reviewer_id == s.id]
	reviewsOfStudents=[r for r in theReviews if r.author_id == s.id]
	#check reviews to make sure they meet requirements
	try:
		scoresGiven={}
		for r in reviewsByStudent:
			if r.data[0]['points'] in scoresGiven:	
				scoresGiven[r.data[0]['points']]+=1
			else:
				scoresGiven[r.data[0]['points']]=1
		if len(scoresGiven)==0:
			print(f"{s.name} has not done reviews yet")
			studentsReviewScores.append({'student': s, 'adj':-10, 'comment': "You lost 10 points for not completing the peer reviews.  "})
		elif len(scoresGiven)>=3:
			studentsReviewScores.append({'student': s, 'adj':0, 'comment': ""})
		else:
			print(f"{s.name} only assigned reviews to {len(scoresGiven)} categories")
			studentsReviewScores.append({'student': s, 'adj':-5, 'comment': "You lost 5 points for not completing the peer reviews according to the instructions (you were supposed to assign at assign submissions to at least 3 different categories).  "})
	except:
		print(s.name, "error")
		for r in reviewsByStudent:
			print(r.data)
		studentsReviewScores.append({'student': s, 'adj':0, 'comment': ""})
	#calculate creation score
	total=0
	cnt=0
	#print(f"{s.name} received scores of: ", end="")
	for r in reviewsOfStudents:
		try:
			total+=r.data[0]['points']
			#print(f"{r.data[0]['points']}, ", end="")
			cnt+=1
		except:
			print("error")
	if cnt>0:
		avg=total/cnt
		studentsCreationScores.append({'student': s, 'avg':int(avg)})
		#print(f" ({avg})")

for sd in studentsCreationScores:
	print(f"{sd['student'].name} scored {sd['avg']}")

studentsWithSuspectReviews=[srs for srs in studentsReviewScores if srs['adj']<0 ]
if len(studentsWithSuspectReviews)>0:
	print("Students who didn't complete reviews or lacked diversity in the review scores they gave:")
	for data in studentsWithSuspectReviews:
		print(data['student'].name, data['comment'])

scoredStudents=[]
if len(studentsCreationScores)>0:
	print("Student Creation Scores:")
	for data in studentsCreationScores:
		s=data['student']
		adjustment=[data['adj'] for data in studentsReviewScores if data['student']==s][0]
		points=data['avg'] + adjustment
		comment=f"Based on the peer reviews (excellent=100, very good=90, good=80, ok=70) you scored {data['avg']} points.  "
		comment+=[data['comment'] for data in studentsReviewScores if data['student']==s][0]
		comment+="To see what effect your score will have on your course grade, find your lowest scoring chapter grade and use the canvas 'what if' feature to replace it with this score.  Once the scores from the final exam retake quizzes have been posted I will replace  your lowest chapter score with this grade.  Until then this project is not reflected in your canvas grade."
		print(f"{s.name}, {points}\n{comment}\n")
		s.points[ga.id]={'curvedTotal': points}
		s.comments[ga.id]=comment
		scoredStudents.append(s)

if confirm("post on canvas? "):
	postGrades(ga, listOfStudents=scoredStudents)

if confirm("Save student data? "):
	utilities.dataToSave['students']=True
	finish()
