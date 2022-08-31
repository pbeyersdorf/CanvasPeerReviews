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
import webbrowser
import copy
import random
import os
import subprocess
import csv
import math
import time

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
criteriaDescription=dict()
sections=dict()
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
		status['message']="Unable to find 'students.pkl'.\nThis file contains student peer review calibation data from \nany past calibrations. If you have done previous calibrations,\nyou should launch python from the directory containing the file"
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
	for student in students:
		sections[student.section]=student.sectionName

	status["initialized"]=True
	#lastAssignment = getMostRecentAssignment()
	return students, graded_assignments, lastAssignment

######################################
# Record what section a student is in
# 
def assignSections(students):
	for section in course.get_sections():
		for user in section.get_enrollments():
			for student in students:
				if user.user_id == student.id:
					student.section=section.id
					student.sectionName=section.name

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
			try:
				assignmentByNumber[int(''.join(list(filter(str.isdigit,graded_assignments[assignment.id].name))))]=graded_assignments[assignment.id]
			except:
				pass
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
		#return
	reviewers=randmoize(students) 
	creations=makeList(creations)
	i=0
	for reviewer in reviewers:
		tic=time.time()
		while (	time.time()-tic < 1 and ((reviewer.id == creations[i%len(creations)].author_id) or  (studentsById[reviewer.id].section != studentsById[creations[i%len(creations)].author_id].section ))):
			i+=1
		if not time.time()-tic  <1:
			#raise Exception("Timeout error assigning calibration reviews - perhaps the professor hasn't yet graded an assignment frmo each section?")
			return
		creation = creations[i%len(creations)]
		print(i,"assigning", str(studentsById[creations[i%len(creations)].author_id].name) +"'s work (", studentsById[creations[i%len(creations)].author_id].sectionName ,") to be reviewed by ", studentsById[reviewer.id].name, "(" ,studentsById[reviewer.id].sectionName , ")" )
		i+=1
		assignPeerReviews(creation, [reviewer]) 

	
######################################
# Takes a student submission and a list of potential reviewers, and the number of reviews 
# to assign and then interacts with canvas to assign that number of reviewers to peer
# review the submission.  It will select reviewers from the beginning of the list of
# potential reviewers skipping over anyone who has already been assigned at least the
# target number of reviews.
#xxx need to ensure reviews are assigned to students in the same section
def assignPeerReviews(creationsToConsider, reviewers="randomize", numberOfReviewers=999999, append=True):
	startTime=time.time()
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'assignPeerReviews'")
		return
	elif not status['gotStudentsWork']:
		getStudentWork()
		
	countAssignedReviews(creations, append=append)
	creationList=makeList(creationsToConsider)
	#countAssignedReviews(creationList) #is this necessary?
	peers=[x for x in students if x.role=='student']
	graders=[x for x in students if x.role=='grader']
	graders=randmoize(graders)
	if reviewers=="randomize":
		peers=randmoize(peers) 
	reviewers=makeList(peers)
	#assign params.numberOfReviews reviews per creation
	for creation in creationList:
		for reviewer in reviewers:
			if not creation.assignment_id in reviewer.reviewCount:
				reviewer.reviewCount[creation.assignment_id]=0
			if (reviewer.reviewCount[creation.assignment_id] < params.numberOfReviews and creation.reviewCount < numberOfReviewers and reviewer.id != creation.user_id and reviewer.section == studentsById[creation.user_id].section):
					creation.create_submission_peer_review(reviewer.id)
					reviewer.reviewCount[creation.assignment_id]+=1
					creation.reviewCount+=1
					print("assigning " + str(reviewer.name)	 + " to review " + str(creation.author.name) + "'s creation")			
	# now that all creations have been assigned the target number of reviews, keep assigning until all students have the target number of reviews assigned
	for reviewer in reviewers:
		tic=time.time()
		while (reviewer.reviewCount[creationList[0].assignment_id] < params.numberOfReviews and time.time()-tic < 1):
			creation=random.choice(creationList)
			if (reviewer.section == studentsById[creation.user_id].section):
				creation.create_submission_peer_review(reviewer.id)
				reviewer.reviewCount[creation.assignment_id]+=1
				creation.reviewCount+=1
				print("assigning " + str(reviewer.name)	 + " to review " + str(creation.author.name) + "'s creation")			
	if len(graders)==0:
		return
	# finally assign to graders
	sections=dict()
	for grader in graders:
		sections[grader.section] = grader.sectionName
	for key in sections:
		thisSectionsGraders=[x for x in students if (x.role=='grader' and x.section == key)]
		thisSectionsCreations=[x for x in creationList if (x.author.section == key)]
		reviewsPerGrader=int(len(thisSectionsCreations)/len(thisSectionsGraders))
		thisSectionsGraders=makeList(thisSectionsGraders)
		#lol(list,sublistSize) takes a list and returns a list-of-lists with each sublist of size sublistSize
		lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)] # see https://stackoverflow.com/questions/4119070/how-to-divide-a-list-into-n-equal-parts-python
		creationsListofList=lol(thisSectionsCreations,reviewsPerGrader)
		# if dividing up the list left a few extras, add them to the last element
		if (len(creationsListofList) > len(thisSectionsGraders)):
			creationsListofList[-2] += creationsListofList[-1]
		print("Assigning reviews to graders of ", sections[key])
		for i,reviewer in enumerate(thisSectionsGraders):
			for creation in creationsListofList[i]:
				if not creation.assignment_id in reviewer.reviewCount:
					reviewer.reviewCount[creation.assignment_id]=0
				if (reviewer.id != creation.user_id ):
					creation.create_submission_peer_review(reviewer.id)
					reviewer.reviewCount[creation.assignment_id]+=1
					creation.graderReviewCount+=1
					print("assigning grader " + str(reviewer.name)	 + " to review " + str(creation.author.name) + "'s creation")			
	
			
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
	assignSections(students)
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
def countAssignedReviews(creations, append=True):
	#when append=True it will check how many review have already been assigned which is slow (takes about a minute).  When append=False it will set the review count to zero.
	global students
	for student in students:
		clearList(student.reviewCount)
	if append:
		print("Checking how many peer reviews each students has already been assigned...")
		for creation in creations:
			for thesePeerReviews in creation.get_submission_peer_reviews():
				if thesePeerReviews.assessor_id in studentsById:
					reviewer=studentsById[thesePeerReviews.assessor_id]
					if not creation.assignment_id in reviewer.reviewCount:
						reviewer.reviewCount[creation.assignment_id]=0				
					reviewer.reviewCount[creation.assignment_id]+=1	
	else:
		for student in students:
			student.reviewCount[creations[0].assignment_id]=0
	
				

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
						alreadyProcessed = any(thisReview.fingerprint() == review.fingerprint() for thisReview in studentsById[creation.user_id].reviewsReceived)
						if not alreadyProcessed:
							studentsById[creation.user_id].reviewsReceived.append(review)
						if creation.assignment_id in studentsById[creation.user_id].regrade: # replace entry
							for i,thisReview in enumerate(studentsById[creation.user_id].reviewsReceived):
								if thisReview.fingerprint() == review.fingerprint() and assessment['assessment_type']=="grading":
									studentsById[creation.user_id].reviewsReceived[i]=review
								
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
							# if not already assigned assignment.multiplier[cid]
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
	cids=dict()
	for student in studentsToCalibrate:
		uncalibratedReviews=False
		for key,thisGivenReview in student.reviewsGiven.items():
			uncalibratedReviews=uncalibratedReviews or (not thisGivenReview.submission_id in student.submissionsCalibratedAgainst)
		if uncalibratedReviews:
			# reduce the weight of previous calibrations
			for cid in student.delta2:
				student.delta2[cid]*=params.weeklyDegradationFactor()
				student.delta[cid]*=params.weeklyDegradationFactor()
				student.numberOfComparisons[cid]*=params.weeklyDegradationFactor()
		for key,thisGivenReview in student.reviewsGiven.items():
			#student.assignmentsCalibrated[thisGivenReview.assignment_id]=datetime.now()
			if not thisGivenReview.submission_id in student.submissionsCalibratedAgainst: #don't bother if we've already calibrated against this review
				student.submissionsCalibratedAgainst[thisGivenReview.submission_id]=True
				for otherReview in reviewsById[thisGivenReview.submission_id]:
					if (otherReview.reviewer_id != student.id): #don't compare this review to itself
						for cid in thisGivenReview.scores:
							cids[cid]=True
							temp=criteriaDescription[cid]
							student.criteriaDescription[cid]=temp
							if not cid in student.delta2:
								student.delta2[cid]=0
								student.delta[cid]=0
								student.numberOfComparisons[cid]=0 
							if otherReview.review_type == "peer_review" and otherReview.reviewer_id in studentsById:
								if (studentsById[otherReview.reviewer_id]).role == 'grader':
									weight=params.gradingPowerForGraders
								else:
									weight=studentsById[otherReview.reviewer_id].getGradingPower(cid); 
							elif otherReview.review_type == "grading":
								weight=params.gradingPowerForInstructors
							if (cid in student.delta2) and (cid in thisGivenReview.scores) and (cid in otherReview.scores):
								student.delta2[cid]+=weight*(thisGivenReview.scores[cid] - otherReview.scores[cid] )**2 
								student.delta[cid]+=weight*(thisGivenReview.scores[cid] - otherReview.scores[cid] ) 
								student.numberOfComparisons[cid]+=weight		
	#		Use the previously calculated rms-like deviation from other reviewers to calculate a grading power
	#		for this student
	for student in students:
		student.updateGradingPower()

	#		Now that all of the students grading powers have been updated, normalize everything so that the average
	#		grading power for all of the students is 1
	for cid in cids:
		total, numberCounted = 0 , 0
		for student in students:
			if cid in student.rms_deviation_by_category: 
				total+=student.getGradingPower(cid)
				numberCounted+=1
		else:
			student.gradingPower[cid]=1
		for student in students:
			if cid in student.rms_deviation_by_category:
				student.gradingPowerNormalizatoinFactor[cid]*=total/numberCounted
			else:
				student.gradingPowerNormalizatoinFactor[cid]=1

	######### Save student data for future sessions #########	
	with open(status['dataDir'] +status['prefix'] + 'students.pkl', 'wb') as handle:
		pickle.dump(students, handle, protocol=pickle.HIGHEST_PROTOCOL)
	status["calibrated"]=True

######################################
# adjust point distribution for a specific assignment
def overrideDefaultPoints(assignment):
	for cid in assignment.criteria_ids():
		val=getNum("How many points (out of 100) should be awarded for '" + criteriaDescription[cid]+ "'?", params.pointsForCid(cid, assignment.id))
		params.pointsForCid(cid,assignment.id ,val)
	#save the parameters
	with open(status['dataDir'] +status['prefix'] + 'parameters.pkl', 'wb') as handle:
		pickle.dump(params, handle, protocol=pickle.HIGHEST_PROTOCOL)	

######################################
# Process a list of students (or all of the students, calling the
# gradeStudent function for each
def grade(assignment, studentsToGrade="All", reviewGradeFunc=None):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'grade'")
		return		
	if isinstance(studentsToGrade, str) and studentsToGrade.lower()=="all":
		for student in makeList(students):
			gradeStudent(assignment, student, reviewGradeFunc)
	else:
		for student in makeList(studentsToGrade):
			gradeStudent(assignment, student, reviewGradeFunc)
	assignment.graded=True
	status["graded"]=True
	msg=assignment.name +  " graded with the following point values:\n"
	for cid in assignment.criteria_ids():
		msg+= "\t(" +str(params.pointsForCid(cid,assignment.id ))+ ") " + criteriaDescription[cid] + "\n"
	log(msg)

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
	# get a list of the criteria ids assessed on this assignment
	#calculate creation grades
	student.gradingExplanation="Creation grade information for " +str(assignment.name) +"\n\n"
	for review in student.reviewsReceived:
		if review.review_type == "grading" and review.assignment_id == assignment.id:
			student.assignmentsGradedByInstructor[assignment.id]=True
			student.gradingExplanation+="This submission was graded by the instructor.\n"
	creationGrade=0
	creationWasReviewed=False
	for cid in assignment.criteria_ids():
		total, numberCount, weightCount = 0, 0, 0
		student.gradingExplanation+=str(criteriaDescription[cid]) + ":\n"
		gradingExplanationLine=""
		multiplier=params.pointsForCid(cid, assignment.id)
		for review in student.reviewsReceived:
			if review.assignment_id == assignment.id:
				weight=0
				creationWasReviewed=True
				role=""
				gradingExplanationLine=""
				if (review.reviewer_id in studentsById):
					role=studentsById[review.reviewer_id].role
				if review.review_type == "peer_review" and not (assignment.id in student.assignmentsGradedByInstructor):
					if role == 'grader':
						weight=params.gradingPowerForGraders
						gradingExplanationLine="Review [G"+ str(review.reviewer_id) +"_" + str(cid) +"] "
					elif role== 'student':
						weight=studentsById[review.reviewer_id].getGradingPower(cid); 
						gradingExplanationLine="Review [P"+ str(review.reviewer_id)+"_" + str(cid) +"] "
				elif review.review_type == "grading":
					gradingExplanationLine="Review [I"+ str(review.reviewer_id)+"_" + str(cid) +"] "
					weight=params.gradingPowerForInstructors
				if cid in review.scores:
					try:
						reviewer=studentsById[review.reviewer_id]
						compensation=reviewer.deviation_by_category[cid]*params.compensationFactor
						compensation=min(compensation, params.maxCompensationFraction* multiplier)
						compensation=max(compensation, -params.maxCompensationFraction* multiplier)
					except:
						compensation=0			
					gradingExplanationLine+=" Grade of {:.2f} with an adjustment for this grader of {:+.2f} and a relative grading weight of {:.2f}".format(review.scores[cid], compensation, weight)
					if not (str(review.reviewer_id)+"_" + str(cid)) in student.gradingExplanation:
						student.gradingExplanation += "    "  + gradingExplanationLine + "\n"
					total+=max(0,min((review.scores[cid] - compensation)*weight, assignment.criteria_points(cid)*weight)) # don't allow the compensation to result in a score above 100% or below 0%%
					weightCount+=weight
					numberCount+=1
		if (weightCount>0):
			creationGrade+=multiplier*total/(weightCount*assignment.criteria_points(cid))
			student.pointsByCriteria[cid]=multiplier*total/(weightCount*assignment.criteria_points(cid))
		else:
			student.pointsByCriteria[cid]=""

	if (not creationWasReviewed) or weightCount==0:
		#If student submitted something but had no reviews
		if student.creations[assignment.id].submitted_at != None:
			creationGrade=100 # Change this
			student.gradingExplanation+=""#"This submission was not reviewed.  Placeholder grade of " + str(creationGrade) + " assigned\n"
			print("No reviews of",student.name,"on assignment",assignment.name, "assigning placeholder grade of", creationGrade)

	#calculate review grades
	delta2=0
	tempDelta=dict()
	tempTotalWeight=dict()
	numberOfComparisons=0
	student.reviewGradeExplanation=""
	for key, thisGivenReview in student.reviewsGiven.items():
		if thisGivenReview.assignment_id == assignment.id:
			for otherReview in reviewsById[thisGivenReview.submission_id]:
				if (otherReview.reviewer_id != student.id): #don't compare this review to itself
					for cid in thisGivenReview.scores:
						if otherReview.review_type == "peer_review":
							try:
								weight=studentsById[otherReview.reviewer_id].getGradingPower(cid); 
								if (studentsById[otherReview.reviewer_id]).role == 'grader':
									weight=params.gradingPowerForGraders
							except:
								weight=1
							
						elif otherReview.review_type == "grading":
							weight=params.gradingPowerForInstructors

						try:
							if cid in tempDelta:
								tempDelta[cid]+=weight*(thisGivenReview.scores[cid] - otherReview.scores[cid] )
								tempTotalWeight[cid]+=weight
							else:
								tempDelta[cid]=weight*(thisGivenReview.scores[cid] - otherReview.scores[cid] )		
								tempTotalWeight[cid]=weight						
							delta2+=weight*((thisGivenReview.scores[cid] - otherReview.scores[cid] )/ assignment.criteria_points(cid))**2
							numberOfComparisons+=weight 
						except:
							status['err']="Key error" 
	for cid in tempDelta:
		student.reviewGradeExplanation+="For '" + str(criteriaDescription[cid]) + "' you graded on average " 
		if (tempDelta[cid]>0.05):
			student.reviewGradeExplanation+=str(int(100*tempDelta[cid]/tempTotalWeight[cid])/100) + " points higher than other graders\n"
		elif (tempDelta[cid]<-0.05):
			student.reviewGradeExplanation+=str(int(-100*tempDelta[cid]/tempTotalWeight[cid])/100) + " points lower than other graders\n"
		else:
			student.reviewGradeExplanation+=" about the same as other graders\n"
	student.reviewGradeExplanation+="Your review grade will improve as it aligns more closely with other graders\n\n"
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
	
	#adjust the points from a scale of 100 down to the number of points for the assingmnet
	digits=int(2-math.log10(assignment.points_possible))
	creationPoints=round(creationGrade*assignment.points_possible/100.0*  params.weightingOfCreation ,digits)
	reviewPoints=round(reviewGrade*assignment.points_possible/100.0 * params.weightingOfReviews ,digits)
	if (digits ==0):
		creationPoints=int(creationPoints)
		reviewPoints=int(reviewPoints)
	totalPoints=creationPoints + reviewPoints
	
	student.grades[assignment.id]={'creation': creationGrade, 'review':  creationGrade, 'total' :totalGrade}
	student.points[assignment.id]={'creation': creationPoints, 'review':  reviewPoints, 'total' :totalPoints}
	percentileRanking=gradingPowerRanking(student, percentile=True)
	student.regradeComments[assignment.id]=(("View the rubric table above to see details of your regrade.  The regraded submissions earned %." + str(digits) +"f points.\n\n") % 
	(creationPoints) )
	student.comments[assignment.id]=student.reviewGradeExplanation
	if (percentileRanking >66):
		student.comments[assignment.id]+=(("\n\nBased on comparisons of your reviews to those of other students the graders and the instructor, you reviewing quality is in the %dth percentile.  Good job - as one of the better graders in the class your peer reviews will carry additional weight.") % (percentileRanking ) )	
	elif (percentileRanking <33):
		student.comments[assignment.id]+=(("\n\nBased on comparisons of your reviews to those of other students the graders and the instructor, you reviewing quality is in the %dth percentile.  You can improve your ranking (and your review scores) by carefully following the grading rubric.") % (percentileRanking ) )	
	else:
		student.comments[assignment.id]+=(("\n\nBased on comparisons of your reviews to those of other students the graders and the instructor, you reviewing quality is in the %dth percentile.") % (percentileRanking ) )	
	student.comments[assignment.id]+=(("If you believe the peer reviews of your work have a significant error, explain in a comment in the next few days and include the word 'regrade' to have it double checked.\n\n  You earned %." + str(digits) +"f out of  %.f points for your submission and %." + str(digits) +"f points out of %.f for your reviews giving you a score of %." + str(digits) +"f points.\n\n") % 
	(creationPoints, 100*params.weightingOfCreation, reviewPoints, 100*params.weightingOfReviews, totalPoints ) )
	
######################################
# find submissions that need to be regraded as based on the word regrade in the comments

def regrade(assignment=None, studentsToGrade="All", reviewGradeFunc=None, recalibrate=True):
	global status
	if not status['initialized']:
		print("Error: You must first run 'initialize()' before calling 'grade'")
		return
	if assignment==None:
		val=-1
		assignmentList=[x for x in assignmentByNumber.values() if (x.graded and not x.regraded)]
		if len(assignmentList) ==1:
			assignment=assignmentList[0]
		else:
			while not val in assignmentByNumber:
				for i,a in assignmentByNumber.items():
					if (a.graded and not a.regraded) or len(assignmentList) ==0:
						if a.id==lastAssignment.id:
							print(str(i)+")",a.name,"<-most recent")
						else:
							print(str(i)+")",a.name)	
				val=getNum()
			assignment=assignmentByNumber[val]
	print("Regrading " + assignment.name + "...")
	regradedStudents=dict()
	keyword="regrade" # if this keyword is in the comments flag the submission for a regrade
	#make list of students needing a regrade
	if studentsToGrade.lower()=="all":
		for student in makeList(students):
			for key in student.creations:
				c = student.creations[key]
				if c.assignment_id == assignment.id and str(c.edit().submission_comments).lower().count(keyword)>1:
					if not (assignment.id in student.regrade):
						regradedStudents[c.edit().id]=student
	else:
		for student in makeList(studentsToGrade):
			for key in student.creations:
				c = student.creations[key]
				if c.assignment_id == assignment.id and str(c.edit().submission_comments).lower().count(keyword)>1:
					if not (assignment.id in student.regrade):
						regradedStudents[c.edit().id]=student
	#process list of students needing a regrade
	for student_key in regradedStudents:
		student=regradedStudents[student_key]
		student.regrade[assignment.id]="Started"
		for key in student.creations:
			c = student.creations[key]
			if c.assignment_id == assignment.id and str(c.edit().submission_comments).lower().count(keyword)>0:
				comments=[com['comment'] for com in c.edit().submission_comments if keyword in com['comment'].lower()]
				print("regrade requested by " + student.name + "for assignment at: ")
				previewUrl=c.edit().preview_url.replace("preview=1&","")
				webbrowser.open(previewUrl)
				print(previewUrl)
				print("With comments: " + "\n\n".join(comments[1:]) + "\n")
				input("Enter any regrade info and comments into the web browser then press enter to continue ")
	print("done regrading.  updating data...")
	status["regraded"]=True
	assignment.regraded=True
	msg=assignment.name +  " regraded with the following point values:\n"
	for cid in assignment.criteria_ids():
		msg+= "\t(" +str(params.pointsForCid(cid,assignment.id ))+ ") " + criteriaDescription[cid] + "\n"
	log(msg)

	getStudentWork(assignment)
	if (recalibrate):
		calibrate()
	grade(assignment, studentsToGrade=list(regradedStudents.values()), reviewGradeFunc=reviewGradeFunc)
	for student_key in regradedStudents:
		student=regradedStudents[student_key]
		student.comments[lastAssignment.id]=student.regradeComments[assignment.id]
		postGrades(assignment, listOfStudents=[student])
		student.regrade[assignment.id]="Done"
	#postGrades(assignment, listOfStudents=list(regradedStudents.values()))
	######### Save student data for future sessions #########	
	with open(status['dataDir'] +status['prefix'] + 'students.pkl', 'wb') as handle:
		pickle.dump(students, handle, protocol=pickle.HIGHEST_PROTOCOL)
	


######################################
# For the assignment given, post the total grade on canvas and post the associated
# comments.	 The optional arguments allow you to suppress posting comments or the grades
def postGrades(assignment, postGrades=True, postComments=True, listOfStudents='all'):
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
	if (listOfStudents=='all'):
		listOfStudents=students
	for student in listOfStudents:
		creation=student.creations[assignment.id]
		print("posting for",student.name )
		if postGrades:
			creation.edit(submission={'posted_grade':student.points[assignment.id]['total']})
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
	nameCol, gradeCol, commentCol= -1 ,-1 ,-1 
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
	global status, criteriaDescription, params
	if ignoreFile:
		params=Parameters()
		params.loadedFromFile=False
	logFile = open(status['dataDir'] +status['prefix'] + 'parameters.log', "a") 	
	logFile.write("----" + str(datetime.now()) + "----\n")

	for key, assignment in graded_assignments.items():
		if assignment != []:
			needInput=False
			for criteria in assignment.rubric:
				criteriaDescription[criteria['id']]=criteria['description']
				if not criteria['id'] in params.multiplier:
					needInput=True
			if needInput:
				print("Need to assign criteria weightings for the rubric assigned to " + assignment.name + ": ")
				for criteria in assignment.rubric:
					if not criteria['id'] in params.multiplier: 
						print("\t" + criteria['description'])
					else:
						print("\t" + criteria['description'] + " (" + str(params.multiplier[criteria['id']]) +")")
					
				for criteria in assignment.rubric:
					criteriaDescription[criteria['id']]=criteria['description']
					if not criteria['id'] in params.multiplier:
						params.multiplier[criteria['id']]=getNum("How many points (out of 100) should\n\t" +criteria['description'] + "\nbe worth? ",limits=[0,100], fileDescriptor=logFile)
						#val=float(input("\nHow many points (out of 100) should\n\t" +criteria['description'] + "\nbe worth? "))
						#params.multiplier[criteria['id']]=val
						#logFile.write(How many points (out of 100) should\n\t" +criteria['description'] + "\nbe worth?: " + str(val))
	if not params.loadedFromFile or ignoreFile:
		weightingOfCreation=getNum("Enter the relative weight of the creation towards the total grade",0.7, fileDescriptor=logFile)
		weightingOfReviews=getNum("Enter the relative weight of the review towards the total grade",0.3, fileDescriptor=logFile)
		total=weightingOfCreation+weightingOfReviews
		params.weightingOfCreation=weightingOfCreation/total
		params.weightingOfReviews=weightingOfReviews/total
		params.numberOfReviews=getNum("How many reviews should be assigned to each student?",3, fileDescriptor=logFile)	
		params.peerReviewDurationInDays=getNum("How many days should the students have to complete their peer reviews?",3, fileDescriptor=logFile)
		params.gradingPowerForInstructors=getNum("How many times greater than a student should an instructors grading be weighted?",10, fileDescriptor=logFile)
		params.gradingPowerForGraders=getNum("How many times greater than a student should  student graders grading be weighted?",5, fileDescriptor=logFile)
		params.halfLife=getNum("How many assignments is the half life for grading power calculations?",4, fileDescriptor=logFile)
		params.compensationFactor=getNum("What compensation factor for grader deviations (0-1)?",1,[0,1], fileDescriptor=logFile)
		if (params.compensationFactor>0):
			params.maxCompensationFraction=getNum("What is the max fractional amount of a score that can be compensated (0-1)?",defaultVal=0.2,limits=[0,1], fileDescriptor=logFile)
		else:
			params.maxCompensationFraction=0;
	logFile.close()
	with open(status['dataDir'] +status['prefix'] + 'parameters.pkl', 'wb') as handle:
		pickle.dump(params, handle, protocol=pickle.HIGHEST_PROTOCOL)
	status["gotParameters"]=True
	return params

######################################
# save data to a log file
def log(msg, display=True):
	fileName=status['dataDir'] + "log.txt"
	if display:
		print(msg, end ="")
	f = open(fileName, "a")
	f.write("----" + str(datetime.now()) + "----\n")
	f.write(msg) 
	f.write("\n\n") 
	f.close()


######################################
# Export the student grades for the given assignment to a file and optionally print
# them on the screen too.		
def exportGrades(assignment=None, fileName=None, delimiter=",", display=False, saveToFile=True):
	#fileName = "gradesheet.csv"
	if fileName==None and assignment!= None:
		fileName="scores for " + assignment.name + ".csv"
	fileName=status['dataDir'] + fileName
	header="Name" + delimiter +"Sortable Name" + delimiter + "ID" + delimiter
	if assignment!=None:
		for cid in assignment.criteria_ids():
			header+='"' + criteriaDescription[cid] + '"' + delimiter #"LO" + str(cid) + delimiter
		header+="Creation" + delimiter + "Review" + delimiter + "Total" + delimiter + "Comment" + delimiter + "Submission Grading Explanation" + delimiter +  "Review Grade Explaantion\n" 
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
			'"' + student.sortable_name + '"' + delimiter + 
			str(student.sis_user_id) + delimiter)
		if assignment!=None:
			points=student.points[assignment.id]			
			for cid in assignment.criteria_ids():
				if cid in student.pointsByCriteria:
					line+=str(student.pointsByCriteria[cid]) + delimiter
				else:
					line+="" + delimiter
			line+=(str(points['creation']) + delimiter + 
				str(points['review']) + delimiter + 
				str(points['total']) + delimiter + 
				'"' + student.comments[assignment.id] + '"' + delimiter +
				'"' + student.gradingExplanation + '"' + delimiter +
				'"' + student.reviewGradeExplanation + '"'
				) + '\n'
		else:
			line+= ',\n'
		if saveToFile:
			f.write(line)
		if display:
			print(line, end ="")
	if saveToFile:
		f.close()
		
######################################
# Select students to be assigned as graders
def assignGraders():
	keepGoing=True
	while keepGoing:
		for (i,student) in enumerate(students):
			print(str(i+1)+")\t" + student.name)
		i=int(input("Choose a student to be a grader (enter the number) or '0' to skip: "))-1
		if (i<1): 
			print("OK,  not assigning any graders")
			return
		if confirm("Assign " + students[i].name + " as a grader?"):
			students[i].role='grader'
		keepGoing=confirm("Assign another student to be a grader?")
	######### Save student data for future sessions #########	
	with open(status['dataDir'] +status['prefix'] + 'students.pkl', 'wb') as handle:
		pickle.dump(students, handle, protocol=pickle.HIGHEST_PROTOCOL)
	return	

######################################
# Get the grading power ranking
def gradingPowerRanking(theStudent="all",cid=0, percentile=False):
	sortedStudents=sorted(students, key = lambda x : x.getGradingPower(cid), reverse=True) 
	if theStudent=="all":
		print("--Best graders--")
		for (i,student) in enumerate(sortedStudents):
			if student.role=='grader':
				print(str(i+1)+")\t" + student.name + " (grader) %.2f -> %.2f" % (student.getGradingPower(cid),params.gradingPowerForGraders))
			else:
				print(str(i+1)+")\t" + student.name + " %.2f" % student.getGradingPower(cid))
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
def gradingDeviationRanking(theStudent="all", cid=0, percentile=False):
	sortedStudents=sorted(students, key = lambda x : x.getDeviation(cid), reverse=True) 
	if theStudent=="all":
		print("--Easiest graders--")
		for (i,student) in enumerate(sortedStudents):
			print(str(i+1)+")\t" + student.name + " %.2f" % student.getDeviation(cid))
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
def announce(subject, body, section="all"):
	if section == "all":
		announcement=course.create_discussion_topic(message=body, title=subject, is_announcement=True)
	else:
		announcement=course.create_discussion_topic(message=body, title=subject, is_announcement=True, specific_sections=section)

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
# Prompt the user for a response and confirm their response before returning it.
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
# Prompt for a number with a default value
def getNum(msg="choose a number", defaultVal=None, limits=None, fileDescriptor=None):
	dafaultString=""
	if defaultVal!=None:
		dafaultString=" [" + str(defaultVal) + "]"
	while True:
		response=input(msg + dafaultString +": ")
		if response=="":
			response=defaultVal
		try:
			val=float(response)
			if limits == None or (val>= limits[0] and val <= limits[1]):
				if fileDescriptor!=None:
					fileDescriptor.write(msg +": " + str(val) + "\n")
				return val
			else:
				print("Your response must be between " + str(limits[0]) + " and " + str(limits[1]))
		except:
			print("Your response must be numeric")			

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

