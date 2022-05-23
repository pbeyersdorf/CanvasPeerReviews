######################################
# Import various class definitions and other modules
from datetime import datetime, timedelta
from canvasapi import Canvas
from CanvasPeerReviews.creation import Creation
from CanvasPeerReviews.student import Student
from CanvasPeerReviews.assignment import GradedAssignment
from CanvasPeerReviews.parameters import Parameters
from CanvasPeerReviews.review import Review
import pickle
import copy
import random
import os
import subprocess
import csv

######################################
# Define some global variables to be used in this module
studentsById=dict()
creationsByAuthorId=dict()
reviewsById=dict()
params=Parameters()
students=[]
creations=[]
solutionURLs=dict()
graded_assignments=dict()
lastAssignment=[]
assignmentByNumber=dict()
professorsReviews=dict()
course=None
LODescription=dict()
params=Parameters()
status={'message': '',
	'err': '', 
	'initialized': False, 
	'gotParameters': False,
	'gotStudentsWork': False, 
	'gotGradedAssignments': False, 
	'gotMostRecentAssignment': False,
	'gotStudents': False,
	'gotSolutionURLs': False,
	'gotReviews': False,
	'calibrated': False,
	'graded': False,
	'posted': False,
	'dataDir': './'}


######################################
# Try loading any cached data
def loadCache():
	global course, status, params, dataDir, students
	status['prefix']="course_" + str(course.id) + "_"
	try:
		with open( status['dataDir'] +status['prefix']+'students.pkl', 'rb') as handle:
			students=pickle.load(handle)
		status['message']="Loaded student data"
	except:
		status['message']="Unable to find 'students.pkl'.\nThis file contains student peer review calibation data from \nany past calibrations. If you have done previous calibrations,\nyou should launch python from the directory contaiing the file"
	try:
		with open(status['dataDir'] +status['prefix']+'parameters.pkl', 'rb') as handle:
			params = pickle.load(handle)
		params.loadedFromFile=True
	except:
		params=Parameters()
		params.loadedFromFile=False 

######################################
# delete the files that cache student data and parameters
def reset():
	global status
	try:
		os.remove(status['dataDir'] +status['prefix']+'students.pkl')
	except:
		pass
	try:
		os.remove(status['dataDir'] +status['prefix']+'parameters.pkl')
	except:
		pass
	try:
		os.remove(status['dataDir'] +status['prefix']+'solution urls.csv')
	except:
		pass

######################################
# get the course data and return students enrolled, a list of assignments 
# with peer reviews and submissions and the most recent assignment
def initialize(CANVAS_URL=None, TOKEN=None, COURSE_ID=None, dataDirectory="./"):
	global course, canvas, students, graded_assignments, status
	status['dataDir']=dataDirectory
	if not os.path.exists(dataDirectory):
		os.makedirs(dataDirectory)
	printCommand=False
	if (CANVAS_URL==None or COURSE_ID==None):
		response=input("Enter the full URL for the homepage of your course: ")
		parts=response.split('/courses/')
		CANVAS_URL=parts[0]
		COURSE_ID=int(parts[1].split('/')[0])
		printCommand=True
	if (TOKEN==None):
		print("Go to canvas->Account->Settings and from the 'Approved Integrations' section, select '+New Acess Token'")
		TOKEN=input("Enter the token here: ")
		printCommand=True
	canvas = Canvas(CANVAS_URL, TOKEN)
	course = canvas.get_course(COURSE_ID)
	if printCommand:
		print("\nIn the future you can use \n\tinitialize('" +CANVAS_URL+ "', '"+TOKEN+"', " + str(COURSE_ID) +")"+"\nto avoid having to reenter this information\n")
	loadCache()
	print(status['message'])
	getStudents(course)
	getGradedAssignments(course)
	getMostRecentAssignment()
	status["initialized"]=True
	#lastAssignment = getMostRecentAssignment()
	return students, graded_assignments, lastAssignment

######################################
# Given an assignment object this will return all of the student submissions
# to that assignment as an array of objects
def getStudentWork(thisAssignment='last'):
	global creations, graded_assignments, status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'getStudentWork'")
		return
	if thisAssignment=='last':
		thisAssignment=graded_assignments['last']
	submissions=thisAssignment.get_submissions()
	clearList(creations)
	for submission in submissions:
		try:
			submission.courseid=thisAssignment.courseid
			submission.reviewCount=0
			submission.author=studentsById[submission.user_id]
			creations.append(Creation(submission))
			studentsById[submission.user_id].creations[thisAssignment.id]=creations[-1]
			creationsByAuthorId[submission.user_id]=creations[-1]			
		except:
			status['err']="key error"
	getReviews(creations)
	status["gotStudentsWork"]=True


######################################
# Go through all of the assignments for the course and return an array of objects
# from only those assignments that are set up to require peer reviews and
# already have student submissions. 
def getGradedAssignments(course):
	assignments = course.get_assignments()
	global graded_assignments
	for i,assignment in enumerate(assignments):
		if (assignment.peer_reviews and assignment.has_submitted_submissions):
			assignment.courseid=course.id
			graded_assignments[assignment.id]=GradedAssignment(assignment)
			assignmentByNumber[int(''.join(list(filter(str.isdigit,graded_assignments[assignment.id].name))))]=graded_assignments[assignment.id]
	status["gotGradedAssignments"]=True


######################################
# Return the most recently due assignment of all the assignments that have peer reviews
def getMostRecentAssignment():
	global lastAssignment
	lastAssignmentID=None
	if len(graded_assignments)==0:
		getGradedAssignments(course)
	minTimeDelta=timedelta(days=3650)
	for key, graded_assignment in graded_assignments.items():
		try:
			thisDelta=datetime.utcnow()-graded_assignment.due_at_date.replace(tzinfo=None)
			if (thisDelta.total_seconds() > 0  and thisDelta < minTimeDelta) :
				minTimeDelta=thisDelta
				lastAssignment=graded_assignment
		except:
			print("Trouble getting date of",graded_assignment,", likely it was an unscedhueld assignment")
	graded_assignments['last']=lastAssignment
	status["gotMostRecentAssignment"]=True


######################################
#This takes a list of submissions which are to be used as calibration reviews
# and assigns one to each student in the class, making sure to avoid assigning
# a calibration to its own author if possible
def assignCalibrationReviews(creations="auto"):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'assignCalibrationReviews'")
		return
	elif not status['gotStudentsWork']:
		getStudentWork()

	if creations=="auto":
		creations=professorsReviews[graded_assignments['last'].id]
		print(creations)
		return
	reviewers=randmoize(students) 
	creations=makeList(creations)
	i=0
	for reviewer in reviewers:
		if (reviewer.id == creations[i%len(creations)].user_id):
			i+=1
		creation =	creations[i%len(creations)]
		i+=1
		assignPeerReviews(creation, [reviewer]) 

	
######################################
# Takes a student submission and a list of potential reviewers, and the number of reviews 
# to assign and then interacts with canvas to assign that number of reviewers to peer
# review the submission.  It will select reviewers from the beginning of the list of
# potential reviewers skipping over anyone who has already been assigned at least the
# target number of reviews.
def assignPeerReviews(creation, reviewers="randomize", numberOfReviewers=999999):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'assignPeerReviews'")
		return
	elif not status['gotStudentsWork']:
		getStudentWork()

	countAssignedReviews(creations)
	creationList=makeList(creation)
	countAssignedReviews(creationList)
	if reviewers=="randomize":
		reviewers=randmoize(students) 
	reviewers=makeList(reviewers)
	#assign params.numberOfReviews reviews per creation
	for creation in creationList:
		for reviewer in reviewers:
			if not creation.assignment_id in reviewer.reviewCount:
				reviewer.reviewCount[creation.assignment_id]=0
			if (reviewer.reviewCount[creation.assignment_id] < params.numberOfReviews and creation.reviewCount < numberOfReviewers and reviewer.id != creation.user_id ):
				creation.create_submission_peer_review(reviewer.id)
				reviewer.reviewCount[creation.assignment_id]+=1
				creation.reviewCount+=1
				print("assigning " + str(reviewer.name)	 + " to review " + str(creation.author.name) + "'s creation")			
	# now that all creations have been assigned the target number of reviews, keep assigning until all students have the target number of reviews assigned
	for reviewer in reviewers:
		while reviewer.reviewCount[creationList[0].assignment_id] < params.numberOfReviews:
			creation=random.choice(creationList)
			creation.create_submission_peer_review(reviewer.id)
			reviewer.reviewCount[creation.assignment_id]+=1
			creation.reviewCount+=1
			print("assigning " + str(reviewer.name)	 + " to review " + str(creation.author.name) + "'s creation")			
			
######################################
# Get a list of all students enrolled in the course.  Return an array of Student objects
def getStudents(course):
	users = course.get_users(enrollment_type=['student'])
	global students
	#clearList(students)
	for user in users:
		user.courseid=course.id
		alreadyAdded=False
		try:
			for student in students:
				if	student.id==user.id:
					alreadyAdded=True
					studentsById[user.id]=student
		except:
			pass
		if not alreadyAdded:
			studentsById[user.id]=Student(user)
			students.append(studentsById[user.id])

	#studentsById[4445567]="Test Student"	
	status["gotStudents"]=True
	return students
	
	
######################################
# Check if the time window for accepting peer reviews for an assignment has passed
def peerReviewingOver(assignment):
	thisDelta=datetime.utcnow()-assignment.due_at_date.replace(tzinfo=None)
	return thisDelta.total_seconds() > params.peerReviewDurationInSeconds()


######################################
# Look for the URL for the assignment solutions in a csv file.	If the file
# isn't found it will generate a template
def getSolutionURLs(fileName="solution urls.csv"):
	global status
	fileName=status['dataDir'] + fileName
	placeholder="solution URLs go here"
	status["gotSolutionURLs"]=True
	print("looking for solution urls in", fileName)
	try:
		success=False
		f = open(fileName, "r")
		lines = f.readlines()
		f.close()
		for line in lines:
			cells=line.split(",")
			for key, assignment in graded_assignments.items():
				if assignment.name in cells[0] and not placeholder in cells[1]:
					solutionURLs[assignment.id]=cells[1].strip()
					success=True
		return success
	except:
		f = open(fileName, "w")
		f.write("Assignment Name, Solution URL\n")
		for key, assignment in graded_assignments.items():
			f.write(assignment.name + ", " + placeholder +"\n")
		f.close()
		subprocess.call(('open', fileName))
		print("Put the solution URLs into the file '" + fileName + "'")
		return False

# ######################################
# Count how many reviews have been assigned to each student using data from Canvas
def countAssignedReviews(creations):
	global students
	for student in students:
		clearList(student.reviewCount)
	for creation in creations:
		for thesePeerReviews in creation.get_submission_peer_reviews():
			if thesePeerReviews.assessor_id in studentsById:
				reviewer=studentsById[thesePeerReviews.assessor_id]
				if not creation.assignment_id in reviewer.reviewCount:
					reviewer.reviewCount[creation.assignment_id]=0				
				reviewer.reviewCount[creation.assignment_id]+=1		
				

######################################
# Process a given student submission finding all of the peer reviews of that submissions
# those peer reviews get attached to the student objects for both the author of the 
# submission and the students performing the reviews.  Nothing is returned. 
def getReviews(creations):
	rubrics=course.get_rubrics()
	for rubric in rubrics:
		rubric=course.get_rubric(rubric.id,include='assessments', style='full')
		if hasattr(rubric, 'assessments'):
			for creation in creations:
				for assessment in rubric.assessments:
					if ((assessment['assessment_type']=='grading' or assessment['assessment_type']=='peer_review') and creation.id == assessment['artifact_id'] ):
						data=assessment['data']
						reviewer_id = assessment['assessor_id']
						review_type = assessment['assessment_type']
						review=Review(review_type, reviewer_id, creation.user_id, creation.assignment_id, creation.id, data)
						studentsById[creation.user_id].reviewsReceived.append(review)
						if creation.id in reviewsById:
							reviewsById[creation.id].append(review)
						else:
							reviewsById[creation.id]=[review]
						if assessment['assessment_type']=='grading':
							if creation.assignment_id in professorsReviews:
								professorsReviews[creation.assignment_id].append(review)
							else:
								professorsReviews[creation.assignment_id]=[review]
						elif reviewer_id in studentsById:
							# if not already assigned xxx
							studentsById[reviewer_id].reviewsGiven[review.submission_id]=review
	status["gotReviews"]=True

######################################
# Compare the peer reviews students gave to the peer reviews of the same submission 
# given by others.	An average deviation is computed using a weighting factor based on 
# the performance of the other students on their previous reviews.	If the submission
# being reviewed was also graded by the instructor, the deviation from the instructor's
# review will more heavily weighted.  The results are save as a "grading power" for the 
# student in the Student object.  This grading power is used for future calibrations,
# and is used as a weighting factor when assigning grades to students they reviewed.
def calibrate(studentsToCalibrate="all"):
	if (studentsToCalibrate=="all"):
		studentsToCalibrate=students
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'calibrate'")
		return
	LOids=dict()
	for student in studentsToCalibrate:
		uncalibratedReviews=False
		for key,thisGivenReview in student.reviewsGiven.items():
			uncalibratedReviews=uncalibratedReviews or (not thisGivenReview.submission_id in student.submissionsCalibratedAgainst)
		if uncalibratedReviews:
			# reduce the weight of previous calibrations
			for LOid in student.delta2:
				student.delta2[LOid]*=params.weeklyDegradationFactor()
				student.delta[LOid]*=params.weeklyDegradationFactor()
				student.numberOfComparisons[LOid]*=params.weeklyDegradationFactor()
		for key,thisGivenReview in student.reviewsGiven.items():
			#student.assignmentsCalibrated[thisGivenReview.assignment_id]=datetime.now()
			if not thisGivenReview.submission_id in student.submissionsCalibratedAgainst: #don't bother if we've already calibrated against this review
				student.submissionsCalibratedAgainst[thisGivenReview.submission_id]=True
				for otherReview in reviewsById[thisGivenReview.submission_id]:
					if (otherReview.reviewer_id != student.id): #don't compare this review to itself
						for LOid in thisGivenReview.scores:
							LOids[LOid]=True
							student.LODescription[LOid]=LODescription[LOid]
							if not LOid in student.delta2:
								student.delta2[LOid]=0
								student.delta[LOid]=0
								student.numberOfComparisons[LOid]=0 
							if otherReview.review_type == "peer_review" and otherReview.reviewer_id in studentsById:
								weight=studentsById[otherReview.reviewer_id].getGradingPower(LOid); 
							elif otherReview.review_type == "grading":
								weight=params.gradingPowerForGraders
							if (LOid in student.delta2) and (LOid in thisGivenReview.scores) and (LOid in otherReview.scores):
								student.delta2[LOid]+=weight*(thisGivenReview.scores[LOid] - otherReview.scores[LOid] )**2 
								student.delta[LOid]+=weight*(thisGivenReview.scores[LOid] - otherReview.scores[LOid] ) 
								student.numberOfComparisons[LOid]+=weight		
	#		Use the previously calculated rms-like deviation from other reviewers to calculate a grading power
	#		for this student
	for student in students:
		student.updateGradingPower()

	#		Now that all of the students grading powers have been updated, normalize everything so that the average
	#		grading power for all of the students is 1
	for LOid in LOids:
		total, numberCounted = 0 , 0
		for student in students:
			if LOid in student.rms_deviation_by_category: 
				total+=student.getGradingPower(LOid)
				numberCounted+=1
		else:
			student.gradingPower[LOid]=1
		for student in students:
			if LOid in student.rms_deviation_by_category:
				student.gradingPowerNormalizatoinFactor[LOid]*=total/numberCounted
			else:
				student.gradingPowerNormalizatoinFactor[LOid]=1

	######### Save student data for future sessions #########	
	with open(status['dataDir'] +status['prefix'] + 'students.pkl', 'wb') as handle:
		pickle.dump(students, handle, protocol=pickle.HIGHEST_PROTOCOL)
	status["calibrated"]=True


######################################
# Process a list of students (or all of the students, calling the
# gradeStudent function for each

def grade(assignment, studentsToGrade="All", reviewGradeFunc=None):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'grade'")
		return
	if studentsToGrade.lower()=="all":
		for student in makeList(students):
			gradeStudent(assignment, student, reviewGradeFunc)
	else:
		for student in makeList(studentsToGrade):
			gradeStudent(assignment, student, reviewGradeFunc)
	status["graded"]=True

######################################
# Go through all submissions for an assignment. If the assignment was created by
# a student in the list of students given, determine a grade for the submission
# based on a weighted average of peer reviews, or using the instructors grade if it
# was graded by the instructor.	 Then look through all the reviews the students in the
# given list of students performed on this assignment and computer a grade for their
# peer reviews based on a weighted average of the deviation from other reviewers.
# finally combine these two grades to get a total grade, and record all three grades
# into the student object, along with comments that can be shared with the student
# explaining the grade		
def gradeStudent(assignment, student, reviewGradeFunc=None):
	# get a list of the Learning Outcome ids assessed on this assignment
	#calculate creation grades
	for review in student.reviewsReceived:
		if review.review_type == "grading" and review.assignment_id == assignment.id:
			student.assignmentsGradedByInstructor[assignment.id]=True
	creationGrade=0
	creationWasReviewed=False
	for LOid in assignment.learning_outcome_ids():
		total, numberCount, weightCount = 0, 0, 0
		for review in student.reviewsReceived:
			if review.assignment_id == assignment.id:
				weight=0
				creationWasReviewed=True
				if review.review_type == "peer_review" and (review.reviewer_id in studentsById) and not (assignment.id in student.assignmentsGradedByInstructor):
					weight=studentsById[review.reviewer_id].getGradingPower(LOid); 
				elif review.review_type == "grading":
					weight=params.gradingPowerForGraders
				if LOid in review.scores:
					try:
					#if review.reviewer_id in studentsById:
						reviewer=studentsById[review.reviewer_id]
						compensation=reviewer.deviation_by_category[LOid]*params.compensationFactor
					except:
					#else:
						compensation=0			
						#print("unable to compensate for reviewer.id=",review.reviewer_id)
					total+=max(0,min((review.scores[LOid] - compensation)*weight, assignment.learning_outcome_points(LOid)*weight)) # don't allow the compensation to result in a score above 100% or below 0%%
					weightCount+=weight
					numberCount+=1
		if (weightCount>0):
			creationGrade+=params.multiplier[LOid]*total/(weightCount*assignment.learning_outcome_points(LOid))
			student.gradesByLO[LOid]=params.multiplier[LOid]*total/(weightCount*assignment.learning_outcome_points(LOid))
		else:
			student.gradesByLO[LOid]=""
	if not creationWasReviewed or weight==0:
		#If student submitted something but had no reviews
		if student.creations[assignment.id].submitted_at != None:
			creationGrade=100 # Change this
			print("No reviews of",student.name,"on assignment",assignment.name, "assigning placeholder grade of", creationGrade)

	#calculate review grades
	delta2=0
	numberOfComparisons=0
	for key, thisGivenReview in student.reviewsGiven.items():
		if thisGivenReview.assignment_id == assignment.id:
			for otherReview in reviewsById[thisGivenReview.submission_id]:
				if (otherReview.reviewer_id != student.id): #don't compare this review to itself
					for LOid in thisGivenReview.scores:
						if otherReview.review_type == "peer_review":
							try:
								weight=studentsById[otherReview.reviewer_id].getGradingPower(LOid); 
							except:
								weight=1
						elif otherReview.review_type == "grading":
							weight=params.gradingPowerForGraders

						try:
							delta2+=weight*((thisGivenReview.scores[LOid] - otherReview.scores[LOid] )/ assignment.learning_outcome_points(LOid))**2
							numberOfComparisons+=weight 
						except:
							status['err']="Key error" 
	rms=2
	if numberOfComparisons!=0:
		rms=(delta2/numberOfComparisons)**0.5
	try:
		reviewCount=student.reviewCount[creation.assignment_id]
	except:
		reviewCount=params.numberOfReviews

	if reviewGradeFunc == None:
		reviewGrade=(student.numberOfReviewsGivenOnAssignment(assignment.id)/reviewCount) * max(0,min(100, 120*(1-rms)))
	else:
		reviewGrade=reviewGradeFunc(rms)
	totalGrade=creationGrade * params.weightingOfCreation + reviewGrade * params.weightingOfReviews
	
	student.grades[assignment.id]={'creation': round(creationGrade,0), 'review':  round(reviewGrade,0), 'total' : round(totalGrade,0)}
	#student.comments[assignment.id]=("Your received " + str(round(creationGrade * params.weightingOfCreation))+ 
	#" points for your creation and " + str(round(totalGrade,0) - round(creationGrade * params.weightingOfCreation)) +
	#" points for your reviews")
	percentileRanking=gradingPowerRanking(student, percentile=True)
	student.comments[assignment.id]=("Your received %d points for your creation and %d points for your reviews.<p>Based on comparisons of your reviews to those of other students and the instructor, you reviewing quality is in the %dth percetile." % 
	(round(creationGrade * params.weightingOfCreation,0),round(totalGrade,0) - round(creationGrade * params.weightingOfCreation,0), percentileRanking ) )
	

######################################
# For the assignment given, post the total grade on canvas and post the associated
# comments.	 The optional arguments allow you to suppress posting comments or the grades
def postGrades(assignment, postGrades=True, postComments=True):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'postGrades'")
		return
	if not status['gotStudentsWork']:
		print("Error: You must first run 'getStudentWork()' before calling 'postGrades'")
		return	
	if not status['graded']:
		if not confirm("You haven't yet called grade() but you are calling postGrades()\nyou will be posting previously saved grades, and may get an error", False):
			return
	for student in students:
		creation=student.creations[assignment.id]
		print("posting for",student.name )
		if postGrades:
			creation.edit(submission={'posted_grade':student.grades[assignment.id]['total']})
		if postComments:
			creation.edit(comment={'text_comment':student.comments[assignment.id]})
	status["posted"]=True
######################################
# Read a CSV file with student names, grades, and comments and upload that data for the
# assignment from which the creations were taken
def postFromCSV(fileName=None, thisAssignment=None):
	global course, creations
	print("getting list of assignments...")
	if thisAssignment==None:
		assignments = course.get_assignments()
		for (i,assignment) in	enumerate(assignments):
			print(str(i+1)+")",assignment.name)
		val=int(input("Choose the assignment index: "))-1
		thisAssignment=assignments[val]
	elif thisAssignment.lower()=='last':
		thisAssignment=graded_assignments['last']
	#getStudentWork(thisAssignment)
	print("accessing "+thisAssignment.name+"...")
	submissions=thisAssignment.get_submissions()
	
	#get student names, scores and comments from CSV file
	csvData=readCSV(fileName)
	nameCol, gradeCol, commentCol= None ,None ,None 
	for (i,col) in	enumerate(csvData[0]):
		if col.strip().lower() == "name":
			nameCol=i
			print(i+1,col,"<- Name")
		elif col.strip().lower() == "grade" or col.strip().lower() == "total":
			gradeCol = i
			print(i+1,col,"<- Grade")
		elif col.strip().lower() == "comment":
			commentCol = i
			print(i+1,col,"<- Comment")
		else:
			print(i+1,col)
	temp=input("Which coulumn number contains the student names? ["+str(nameCol+1)+"] ")	
	if temp!="":
		nameCol=int(temp)-1
	temp=input("Which coulumn number contains the student grades (0 for none)? [" +str(gradeCol+1)+"] ")
	if temp!="":	
		gradeCol=int(temp)-1
	temp=input("Which coulumn number contains the comments (0 for none)? [" +str(commentCol+1)+"] ")
	if temp!="":	
		commentCol=int(temp)-1
	for submission in submissions:
		if submission.user_id in studentsById:
			student=studentsById[submission.user_id]
			for (j, row) in enumerate(csvData):
				try:
					if ((student.name == row[nameCol] or student.sortable_name == row[nameCol])
					 and submission.assignment_id == thisAssignment.id):
						msg="posting "+ student.name + ":\n"
						if gradeCol!=-1:
							submission.edit(submission={'posted_grade':row[gradeCol]})
							msg+="\tscore: " + row[gradeCol] +"\n"
						if commentCol!=-1:
							submission.edit(comment={'text_comment':row[commentCol]})
							msg+="\tcomment: '" + row[commentCol] +"'\n"
						print(msg, end="")

				except:
					status['err']="unable to process test student"
	status["posted"]=True

######################################
# If the grading parameters were not available in a saved file, prompt the user
# for these.  These parameters are used to define things like the weighting of
# various rubric criteria, and the weighting of the submission score versus the 
# review score.	 The results get saved to a file so they don't need to be 
# reentered everytime the script is run
def getParameters(ignoreFile=False):
	global status, LODescription, params
	if ignoreFile:
		params=Parameters()
		params.loadedFromFile=False
	for key, assignment in graded_assignments.items():
		for outcome in assignment.rubric:
			LODescription[outcome['outcome_id']]=outcome['description']
			if not outcome['outcome_id'] in params.multiplier:
				val=float(input("\nHow many relative points should\n\t" +outcome['description'] + "\nbe worth? "))
				params.multiplier[outcome['outcome_id']]=val	
	if not params.loadedFromFile or ignoreFile:
		val=float(input("\nWhat should be the relative weight of the creation towards the total grade? "))
		weightingOfCreation=val
		val=float(input("\nWhat should be the relative weight of the review towards the total grade? "))
		weightingOfReviews=val
		total=weightingOfCreation+weightingOfReviews
		params.weightingOfCreation=weightingOfCreation/total
		params.weightingOfReviews=weightingOfReviews/total
		val=int(input("\nHow many reviews should be assigned to each student? "))
		params.numberOfReviews=val	
		val=float(input("\nHow many days should the students have to complete their peer reviews? "))
		params.peerReviewDurationInDays=val
		val=int(input("\nHow many times greater than a student should an instructors grading be weighted? "))
		params.gradingPowerForGraders=val
		val=float(input("\nHow many assignments is the half life for grading power calculations? "))
		params.halfLife=val
		val=-1
		while val<0 or val >1:
			val=float(input("\nWhat compensation factor for grader deviations (0-1)? "))
		params.compensationFactor=val
		
	with open(status['dataDir'] +status['prefix'] + 'parameters.pkl', 'wb') as handle:
		pickle.dump(params, handle, protocol=pickle.HIGHEST_PROTOCOL)
	status["gotParameters"]=True
	return params

######################################
# Export the student grades for the given assignment to a file and optionally print
# them on the screen too.		
def exportGrades(assignment=None, fileName=None, delimiter=",", display=False, saveToFile=True):
	fileName = "gradesheet.csv"
	if fileName==None and assignment!= None:
		fileName="scores for " + assignment.name + ".csv"
	fileName=status['dataDir'] + fileName
	header="Name" + delimiter +"Sortable Name" + delimiter + "ID" + delimiter
	if assignment!=None:
		for LOid in assignment.learning_outcome_ids():
			header+="LO " + str(LOid) + delimiter
		header+="Creation" + delimiter + "Review" + delimiter + "Total" + delimiter + "Comment\n" 
	else:
		header+="Grade, Comment\n"
	if saveToFile:
		f = open(fileName, "w")
		f.write(header) 
	if display:
		print(fileName[:-4])
		print(header)

	for (i,student) in enumerate(students):
		line=(student.name + delimiter + 
			student.sortable_name + delimiter + 
			str(student.sis_user_id) + delimiter)
		if assignment!=None:
			grades=student.grades[assignment.id]			
			for LOid in assignment.learning_outcome_ids():
				if LOid in student.gradesByLO:
					line+=str(student.gradesByLO[LOid]) + delimiter
				else:
					line+="" + delimiter
			line+=(str(grades['creation']) + delimiter + 
				str(grades['review']) + delimiter + 
				str(grades['total']) + delimiter + '"' +
				student.comments[assignment.id] ) + '"\n'
		else:
			line+= ',\n'
		if saveToFile:
			f.write(line)
		if display:
			print(line, end ="")
	if saveToFile:
		f.close()
		

######################################
# Get the grading power ranking
def gradingPowerRanking(theStudent="all",LOid=0, percentile=False):
	sortedStudents=sorted(students, key = lambda x : x.getGradingPower(LOid), reverse=True) 
	if theStudent=="all":
		print("--Best graders--")
		for (i,student) in enumerate(sortedStudents):
			print(str(i+1)+")\t" + student.name + " %.2f" % student.getGradingPower(LOid))
		print("--Worst graders--")
		return
	rank=0
	for student in sortedStudents:
		rank+=1
		if theStudent.id == student.id:
			break
	if percentile:
		return int(round(100.0*(len(sortedStudents)-rank)/len(sortedStudents),0))
	return rank

######################################
# Get the grading deviation ranking
def gradingDeviationRanking(theStudent="all", LOid=0, percentile=False):
	sortedStudents=sorted(students, key = lambda x : x.getDeviation(LOid), reverse=True) 
	if theStudent=="all":
		print("--Easiest graders--")
		for (i,student) in enumerate(sortedStudents):
			print(str(i+1)+")\t" + student.name + " %.2f" % student.getDeviation(LOid))
		print("--Hardest graders--")
		return
	rank=0
	for student in sortedStudents:
		rank+=1
		if theStudent.id == student.id:
			break
	if percentile:
		return int(round(100.0*(len(sortedStudents)-rank)/len(sortedStudents),0))
	return rank
			


######################################
# Send an announcement to the canvas course			
def announce(subject, body):
	announcement=course.create_discussion_topic(message=body, title=subject, is_announcement=True)

######################################
# Send a canvas message to a student or list of students.		
def message(theStudents, body):
	studentList=makeList(theStudents)
	for student in studentList:
		canvas.create_conversation(student.id, body)
######################################
# Read a CSV file and return the data as an array
def readCSV(fileName=None):
	if fileName==None:	
		fileName = input('Select the CSV file to read: ').strip().replace("\\","") # show an "Open" dialog box and 
	data=[]
	with open(fileName, mode ='r') as file:
		csvFile = csv.reader(file)
		for lines in csvFile:
			data.append(lines)
		pass
	return data

######################################
# Prompt the user for a responce and confirm their response before returning it.
def confirm(msg, requireResponse=False):
	confirmationResponse=""
	if not requireResponse:
		print(msg)
		confirmationResponse=input("'ok' to accept: " )
		return	(confirmationResponse == 'ok')
	while confirmationResponse!='ok':
		response=input(msg)
		confirmationResponse=input("You entered '" + str(response) +"'\n'ok' to accept: " )
	return response


######################################
# List all objects in an array and prompt the user to select one.  
# Once they confirm their choice it will be returned

def select(objArray, prompt="Choose one"):
	for i,obj in enumerate(objArray):
		print(i , obj)

	confirmed=False
	while not confirmed:	
		response=input(prompt + ": ")
		selection=int(response)
		response = input("type 'ok' to confirm or choose a new value" + str(objArray[selection]) + ": " ) 
		confirmed = (response == 'ok')
	return objArray[selection]

######################################
# Take an array and return a shuffled version of it 
def randmoize(theArray):
	newArray=[]
	for theElement in theArray:
		newArray.append(theElement)
	random.shuffle(newArray)
	return newArray
	
######################################
# Take an object or list of objects, and return a list of objects
def makeList(obj):
	if not type(obj) == list:
		return	[obj]
	return obj

######################################
# clear a list without redefining it.  Allows it to be kept in global scope
def clearList(lst):
	if	type(lst) == list:
		while lst:
			lst.pop()
	elif type(lst) ==dict:
		while lst:
			lst.popitem()

