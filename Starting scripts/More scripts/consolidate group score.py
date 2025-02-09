#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
# if no assignments have yet been graded then prompt for graders
#assignGraders()


#from datetime import datetime
import pytz

print('''
This script will go allow you to pick one assignment group in canvas (for 
example 'Ch 5 work').  It will attempt to compute a score for the group as 
a whole (by summing up all the points earned divided by points possible for 
every assignment in the group.  If there is an ungraded missing assignment 
the score for the group will be zero.

It will then create a new group to post scores based on the name of the 
assignment group (for example 'Ch 5 scores') replacing the last word in the
original assignment group name with the word 'scores'.  It will create two
assignments in this group - one for the score from the assignment group, 
and one to serve as a place to upload a test.  It will set the group to be
worth 5% of the course grade and set a rule to drop the lowest score.
''')


course=utilities.course
groups=course.get_assignment_groups()
assignments = course.get_assignments()
#rubrics=course.get_rubrics()
#rubric=rubrics[0].data
#rubric_settings={'id': rubric.id, 'title': rubric.title, 'points_possible': rubric.points_possible, 'free_form_criterion_comments': rubric.free_form_criterion_comments, 'hide_score_total': rubric.hide_score_total, 'hide_points': False}
#for groups like "ch 6 work", "ch 6 tests", "ch 6 grade" the possible suffixes:
sufixes={'work': 'work', 'score': 'score'}

submissionByUA=dict()
groupById=dict()
for i, group in enumerate(groups):
	groupById[group.id]=group

def getUnit():
	coreCount=dict()
	for i, group in enumerate(groups):
		thisCore=" ".join(group.name.split(" ")[0:-1])
		if not thisCore in coreCount:
			coreCount[thisCore]=0
		coreCount[thisCore]+=1
	#cores=[key for key in coreCount if coreCount[key]>1 and len(key)>0]
	cores=[key for key in coreCount if coreCount[key]>0 and len(key)>0]
	for i,key in enumerate(cores):
		print(i+1,key)
	val=int(input("Choose a unit: "))-1
	print(cores[val])
	return cores[val]

#get all submissions on all assignments and organize them by groupID, 	
def getWorkInGroup(group):
	for a in assignments:
		if a.assignment_group_id==group.id:
			print("Getting submissions for " + a.name + " ("  + groupById[group.id].name +")")
			submissions=a.get_submissions()
			for sub in submissions:
				if sub.user_id not in submissionByUA:
					submissionByUA[sub.user_id]=dict()
				submissionByUA[sub.user_id][a.id]=sub
	
# return the students scores for each group id
# if any assignments in a group have a point value, it will return the average score
# otherwise it will return 100 if no submissions are missing, or zero if there are missing submissions
def checkStudentProgress(userID, group):
	if isinstance(userID,Student):
		userID=userID.id
	returnVal=dict()
	#for group in groups:
	key=group.id
	#key=group.name
	if userID not in studentsById:
		print("unable to find user")
		return
	#print(f"checking {groupById[group.id]} for {studentsById[userID].name}")
	assignmentsInGroup=[a for a in assignments if a.assignment_group_id==group.id]
	missedAssignments=False
	pointsReceived=0
	pointsPossible=0
	numberOfAssignments=0
	for a in assignmentsInGroup:
		try:
			pastDue=(datetime.utcnow().replace(tzinfo=pytz.UTC)-a.due_at_date).total_seconds()>0
			if userID not in submissionByUA:
				print("Need to get work")
				getWorkInGroup(group)
			elif a.id not in submissionByUA[userID]:
				print("Looking up work in " + group.name)
				getWorkInGroup(group)
			sub=submissionByUA[userID][a.id]
			if a.grading_type != "not_graded" and a.published and pastDue:
				numberOfAssignments+=1
				if sub.missing:
					missedAssignments=True
					pointsPossible+=a.points_possible
					#print(f"    missing submission on {a.name}")
				elif sub.score !=None :
					pointsReceived+=sub.score
					pointsPossible+=a.points_possible
					#print(f"    scored {sub.score} out of {a.points_possible} on {a.name}")
				else:
					pass
					#print(f"    submitted  {a.name}")
		except AttributeError:
			#print(f"trouble getting details for assignment {a.name}")
			pass
	if pointsPossible>0:
		returnVal[key]= round(100.0*pointsReceived/pointsPossible)
	elif missedAssignments:
		returnVal[key]= 0
	else:
		if numberOfAssignments==0:
			print("None")
			returnVal[key]= None
		else:
			returnVal[key]= 100
	return returnVal[key]
	
#need to check related groups ('ch 5 work', 'ch 5 tests', ch 5 grade')
unitName=getUnit()

studendtProgress=dict()

def postWorkScore(student):
	if student.id not in studendtProgress:
		studendtProgress[student.id]=dict()
	if unitName not in studendtProgress[student.id]:
		studendtProgress[student.id][unitName]=dict()		

	workGroupName=(unitName+ " " + sufixes['work'])
	workGroupList=[grp for grp in groups if grp.name == workGroupName]
	scoreGroupName=(unitName+ " " + sufixes['score'])
	scoreGroupList=[grp for grp in groups if grp.name == scoreGroupName]

	if len(scoreGroupList)==0:
		print(f"creating assignment group '{scoreGroupName}'")
		groupForWorkScore=course.create_assignment_group(name=scoreGroupName, group_weight = 5, rules={'drop_lowest': 1}) 
	else:
		groupForWorkScore=scoreGroupList[0]
	
	if len(workGroupList)>0:
		#print(f"Inspecting work in group {workGroupName}")
		workgGroup=workGroupList[0]
		sp=studendtProgress[student.id][unitName]['work']=checkStudentProgress(student,workgGroup)
		assignmentName=unitName + " " + sufixes['work'] + " score"
		aList=[a for a in assignments if a.name==assignmentName]
		if len(aList)==0:
			print(f"Creating a new assignment named {assignmentName} in group")
			assignmentForWorkScore = course.create_assignment({
			'name': assignmentName,
			'points_possible': 100,
			'due_at': datetime.now(),
			'description': 'Total score for the work done on ' + unitName,
			'published': True,
			'assignment_group_id': groupForWorkScore.id
			}) 
			assignmentForTestScore = course.create_assignment({
			'name': unitName + " test",
			'points_possible': 100,
			'description': 'Test/Quiz for ' + unitName,
			'published': False,
			'assignment_group_id': groupForWorkScore.id,
			'submission_types': ['online_upload'],
			'peer_reviews' : True,
			'automatic_peer_reviews' : False,
			'anonymous_peer_reviews' : True,
			'use_rubric_for_grading' : False,
			'rubric' : rubric,
			'rubric_settings' : rubric_settings
			}) 
			submissions=assignmentForWorkScore.get_submissions()
			for sub in submissions:
				if sub.user_id not in submissionByUA:
					submissionByUA[sub.user_id]=dict()
				submissionByUA[sub.user_id][assignmentForWorkScore.id]=sub
		else:
			assignmentForWorkScore=aList[0]
		printLine("Posting a grade of " +str(sp) +" to " + assignmentForWorkScore.name + " for " + student.name,newLine=False)
		#print(f"\rPosting a grade of {sp} to {assignmentForWorkScore.name} for {student.name}" )
		if assignmentForWorkScore.id not in submissionByUA[student.id]:
			getWorkInGroup(groupForWorkScore)
		sub=submissionByUA[student.id][assignmentForWorkScore.id]
		sub.edit(submission={'posted_grade':sp})

	if len(workGroupList)==0: 
		print(f"Unable to find work group {workGroupName}")
		studendtProgress[student.id][unitName]['work']=None
		
for s in students:
	postWorkScore(s)
printLine("Done! make sure to check the gradebook ",newLine=False)

