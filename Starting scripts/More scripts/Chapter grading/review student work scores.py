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
	quizDueTime=input("Enter the time the quizzes should be due in 24-hour format, i.e. '9:25'")
	params.quizDueTime=quizDueTime
	saveData(['parameters'])


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
	codes=[chr(i+65) for i in range(26)]
	for j in range(26):
			codes+=[chr(j+65)+chr(i+65) for i in range(26)]			
	for i, group in enumerate(groups):
		thisCore=" ".join(group.name.split(" ")[0:-1])
		if not thisCore in coreCount:
			coreCount[thisCore]=0
		coreCount[thisCore]+=1
	#cores=[key for key in coreCount if coreCount[key]>1 and len(key)>0]
	cores=[key for key in coreCount if coreCount[key]>0 and len(key)>0]	
	unitByNumber=dict()
	for i,core in enumerate(cores):
		try:
			if int(''.join(list(filter(str.isdigit,core)))) not in unitByNumber:
				unitByNumber[int(''.join(list(filter(str.isdigit,core))))]=core
		except Exception:
			pass
	#list all of the units by number if it has a number or letter otherwise.
	i=0
	unitKeyByNumber=dict()
	for core in cores:
		if  core in unitByNumber.values():
			iStr=str([num for num in unitByNumber if unitByNumber[num]==core ][0]) +")"
		else:
			iStr=codes[i]+")"
			i+=1	
		print(f"\t{iStr:<4}{core}")	
		unitKeyByNumber[iStr[:-1]]=core
	val=input("Choose a unit: ")
	print(f"You have chosen {unitKeyByNumber[val]}")
	return unitKeyByNumber[val]

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
	msg="\n"+studentsById[userID].name +"\n"
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
			if a.published and pastDue:
				numberOfAssignments+=1
				if sub.missing:
					missedAssignments=True
					try:
						pointsPossible+=a.points_possible
					except:
						pass
					#print(f"    missing submission on {a.name}")
				elif sub.score !=None :
					pointsReceived+=sub.score
					try:
						pointsPossible+=a.points_possible
					except:
						pass
					#print(f"    scored {sub.score} out of {a.points_possible} on {a.name}")
				else:
					pass
					#print(f"    submitted  {a.name}")
			msg+="\t"+ str(a.name) + " [" + str(sub.score) + "]\n"
		except AttributeError:
			#print(f"trouble getting details for assignment {a.name}")
			pass
	if pointsPossible>0:
		returnVal[key]= round(1.0*maxWorkScore*pointsReceived/(pointsPossible-extraCreditPoints))
	elif missedAssignments:
		returnVal[key]= 0
	else:
		if numberOfAssignments==0:
			print("None")
			returnVal[key]= None
		else:
			returnVal[key]= maxWorkScore
	print(msg)
	return returnVal[key]
	
#need to check related groups ('ch 5 work', 'ch 5 tests', ch 5 grade')
unitName=getUnit()

workGroupName=(unitName+ " " + sufixes['work'])
workGroupList=[grp for grp in groups if grp.name == workGroupName]
group=workGroupList[0]
assignmentsInGroup=[a for a in assignments if a.assignment_group_id==group.id]
print("Assignments in this group (and point values):")
for a in assignmentsInGroup:
	if "bonus" in a.name.lower() or "extra" in  a.name.lower():
		print(f"    {Fore.RED}{a.points_possible}  {a.name}{Style.RESET_ALL}")
	else:
		print(f"    {a.points_possible}  {a.name}")
#extraCreditPoints=float(inputWithTimeout("How many points should be considered extra credit?", default=0))

studentProgress=dict()

while True:
	name=input("Enter the name (or partial name) of a student whose work score you want to review: ")
	s=selectStudentByName(name)
	checkStudentProgress(s, group)
