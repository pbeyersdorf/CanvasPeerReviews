#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
try:
	maxWorkScore=params.maxWorkScore
except:
	maxWorkScore=getNum("Enter max score out of 100 to assign for completed work",  defaultVal=70, limits=[0,100])
	params.maxWorkScore=maxWorkScore
	saveData(['parameters'])
try:
	percentPerUnit=params.percentPerUnit
except:
	percentPerUnit=getNum("Enter the percentage of the total course grade each unit should be assigned",  defaultVal=6.25, limits=[0,100])
	params.percentPerUnit=percentPerUnit
	saveData(['parameters'])
try:
	quizDueTime=params.quizDueTime
except:
	quizDueTime=input("Enter the time the quizzes should be do in 24-hour format, i.e. '9:25'")
	params.quizDueTime=quizDueTime
	saveData(['parameters'])
FinalDueDate=None

#from datetime import datetime
import pytz

print('''
This script will allow you to pick one assignment group in canvas (for 
example 'Ch 5 work').  It will attempt to compute a score for the group as 
a whole (by summing up all the points earned divided by points possible for 
every assignment in the group.)  If there is an ungraded missing assignment 
the score for the group will be zero.

It will then create a new group to post scores based on the name of the 
assignment group (for example 'Ch 5 scores') replacing the last word in the
original assignment group name with the word 'scores'.  It will create two
assignments in this group - one for the score from the assignment group, 
and one to serve as a place to upload a test.  It will set the group to be
worth [percentPerUnit] of the course grade and set a rule to drop the lowest score.
''')


course=utilities.course
groups=course.get_assignment_groups()
assignments = course.get_assignments()
rubrics=course.get_rubrics()
rubric=rubrics[0]#.data
rubric_settings={'id': rubric.id, 'title': rubric.title, 'points_possible': rubric.points_possible, 'free_form_criterion_comments': rubric.free_form_criterion_comments, 'hide_score_total': rubric.hide_score_total, 'hide_points': False}
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
	
def updateGradebook(student=None):
	global quizDueTime, FinalDueDate

	workGroupName=(unitName+ " " + sufixes['work'])
	workGroupList=[grp for grp in groups if grp.name == workGroupName]
	scoreGroupName=(unitName+ " " + sufixes['score'])
	scoreGroupList=[grp for grp in groups if grp.name == scoreGroupName]

	if len(scoreGroupList)==0:
		print(f"creating assignment group '{scoreGroupName}'")
		#groupForWorkScore=course.create_assignment_group(name=scoreGroupName, group_weight = percentPerUnit, rules={'drop_lowest': 1}) 
		groupForWorkScore=course.create_assignment_group(name=scoreGroupName, group_weight = percentPerUnit) 
	else:
		groupForWorkScore=scoreGroupList[0]
	
	if len(workGroupList)>0:
		#print(f"Inspecting work in group {workGroupName}")
		workgGroup=workGroupList[0]
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
			year=datetime.now().strftime("%y")
			tomorrow=datetime.now()+timedelta(days=1)
			dayMonth=input(f"Enter date for the unit/chapter {unitName} quiz [{tomorrow.strftime('%m/%d')}]: ")
			if dayMonth=="":
				dayMonth=tomorrow.strftime('%m/%d')
			val=input(f"Enter the time the quiz is due (in 24-hour format) [{quizDueTime}]: ")
			if val!="":
				quizDueTime=val
			dueDate=datetime.strptime(dayMonth +"/"+ year+ " " + quizDueTime, '%m/%d/%y %H:%M')
			assignmentForTestScore = course.create_assignment({
			'name': unitName + " quiz",
			'points_possible': 100,
			'due_at': dueDate,
			'description': 'Test/Quiz for ' + unitName,
			'published': False,
			'assignment_group_id': groupForWorkScore.id,
			'submission_types': ['online_upload'],
			'peer_reviews' : True,
			'automatic_peer_reviews' : False,
			'anonymous_peer_reviews' : True,
			'use_rubric_for_grading' : False,
			'rubric' : rubric.data,
			'rubric_settings' : rubric_settings
			}) 
			groupForWorkScore.edit(rules={'drop_lowest': 1})
			
			# Create a final retake quiz
			if FinalDueDate==None:
				FinalDueDate=input("Enter the date and time the final exam quizzes should be uploaded\n use 24 hour format like ('5/17/23 9:30'): ")
				FinalDueDate=datetime.strptime(FinalDueDate, '%m/%d/%y %H:%M')
			assignmentForTestScore = course.create_assignment({
			'name': unitName + " quiz - Final Retake",
			'points_possible': 100,
			'due_at': FinalDueDate,
			'description': 'Final Test/Quiz retake for ' + unitName,
			'published': False,
			'assignment_group_id': groupForWorkScore.id,
			'submission_types': ['online_upload'],
			'peer_reviews' : True,
			'automatic_peer_reviews' : False,
			'anonymous_peer_reviews' : True,
			'use_rubric_for_grading' : False,
			'rubric' : rubric.data,
			'rubric_settings' : rubric_settings
			}) 
		else:
			assignmentForWorkScore=aList[0]
		print("Assignments created.  You may need to manually add a grading rubric")

#need to check related groups ('ch 5 work', 'ch 5 tests', ch 5 grade')
while True:
	unitName=getUnit()
	studendtProgress=dict()	
	updateGradebook()	

printLine("Done! make sure to check the gradebook ",newLine=False)