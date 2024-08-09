#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from CanvasPeerReviews import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

print(''' 
This script will take an assignment such as "Instructional Video #2" and get
both the student scores for that assignment and the comments (in an attempt
to figure out what chapter the submission was for) and then generate
a list of assignmetns in the chapter groups that have the same base name 
(such as "Instructional Video (Ch 5)") creating the assignment if one can't
be found.  Then it copies the student grade from the source assignment into 
that assignment.

''')
import requests, os, re, random

course=utilities.course
groups=course.get_assignment_groups()
assignments = course.get_assignments()
submissionByUA=dict()
groupById=dict()
for i, group in enumerate(groups):
	groupById[group.id]=group

#get all submissions on all assignments and organize them by groupID, 	
def getWorkInGroup(group):
	for a in assignments:
		if a.assignment_group_id==group.id:
			#print("Getting submissions for " + a.name + " ("  + groupById[group.id].name +")")
			submissions=a.get_submissions()
			for sub in submissions:
				if sub.user_id not in submissionByUA:
					submissionByUA[sub.user_id]=dict()
				submissionByUA[sub.user_id][a.id]=sub


#get the source assignment
nonChapterGroupIds= [g.id for g in groups if "Ch" not in g.name]
codes=[chr(i+65) for i in range(26)]
nonChapterAssignments=[a for a in assignments if a.assignment_group_id in nonChapterGroupIds]
sourceAssignment=None
while sourceAssignment==None or not confirm(f"You have chosen {sourceAssignment.name} as the source assignment"):
	for i, a in enumerate(nonChapterAssignments):
		print(codes[i], a.name)
	val=ord(input("Enter an assignment that has the source grades: ").upper())-65
	sourceAssignment=nonChapterAssignments[val]

print(f"Make sure {sourceAssignment.name} gradging is set to 'points'")

#get student grades on source assignment
print("Getting submissions for " + sourceAssignment.name)
submissions=sourceAssignment.get_submissions()
for sub in submissions:
	if sub.user_id not in submissionByUA:
		submissionByUA[sub.user_id]=dict()
	submissionByUA[sub.user_id][sourceAssignment.id]=sub
getStudentWork(sourceAssignment)
creationsWithContent=[c for c in creations if c.attempt != None]



# get the chapter number for each submission
for c in creationsWithContent:
	allCreationComments=c.edit().submission_comments
	authorComments=[]
	c.chapter=None
	theseComments=studentsById[c.author_id].name + "'s submissioni comments:\n"
	for comment in allCreationComments:
		cmnt=comment['comment']
		start=0
		end=0
		#comment should be of hte form '6.33-6.34 (charges on conductors)'
		try:
			if comment['author_id'] == c.user_id :
				theseComments+="\t" + cmnt + "\n"
				if "(" in cmnt and ")" in cmnt:
					c.chapter=re.findall("\d+\.\d+",cmnt.split("(")[0])[0].split(".")[0]
		except:
			pass
	if c.chapter==None:
		print(theseComments)
		val=input(f"Enter the chapter that {studentsById[c.author_id].name } dia video on: ")
		c.chapter=val.strip()



#get the assignment target base name
assignmentBaseName=sourceAssignment.name
while not confirm(f"\nUse {assignmentBaseName} as the target assignment base name?"):
	assignmentBaseName=input("Enter the target assignment base name: ")


# get the score groups 
#for groups like "ch 6 work", "ch 6 tests", "ch 6 grade" the possible suffixes:
sufixes={'work': 'work', 'score': 'score'}
coreCount=dict()
for i, group in enumerate(groups):
	thisCore=" ".join(group.name.split(" ")[0:-1])
	if not thisCore in coreCount:
		coreCount[thisCore+ " " + sufixes['score']]=0
	coreCount[thisCore + " " + sufixes['score']]+=1
scoreGroups=[g for g in groups if g.name in list(coreCount.keys())]

#creat a dictionary of all of the target assignments
#add an assignment to the score groups if it doens't exist
targetAssignments=dict()
for group in scoreGroups:
	core=group.name.replace(sufixes['score'],"").strip()
	assignmentName=assignmentBaseName + " (" + core +")"
	if assignmentName not in [a.name for a in assignments]:	
		print(f"Creating assignmetn {assignmentName} for the list of target assignmetns")
		targetAssignments[group.id]=course.create_assignment({
		'name': assignmentName,
		'points_possible': 100,
		'due_at': datetime.now(),
		'description': "Score for the '" + sourceAssignment.name +"' assignment applied to " + core,
		'published': False,
		'assignment_group_id': group.id
		}) 
	else:
		targetAssignments[group.id]=targetAssignment=[a for a in assignments if a.name==assignmentName][0]
		print(f"Adding assignment {targetAssignment.name} to the list of target assignmetns")
	getWorkInGroup(group)

def updateGradebook(student, dryrun=False):
	#get students grade on source assignment
	sourceSub=submissionByUA[student.id][sourceAssignment.id]
	sp=sourceSub.score
	chapter="the chapter is unknown"
	try:
		chapter=[c for c in creationsWithContent if c.author_id == sourceSub.user_id][0].chapter
	except:
		#print(f"No submission for {student.name}")
		return

	#get the target assignment in this group
	keys=[i for i in targetAssignments if ("(ch " + chapter + ")") in targetAssignments[i].name.lower()]	
	if len(keys)==1:
		key=keys[0]
		targetAssignment=targetAssignments[keys[0]]
	else:
		keys=[i for i in targetAssignments if chapter in targetAssignments[i].name]
		if len(keys)==0:
			keys=[i for i in targetAssignments]
		print(f"\nKey    Assignment   (looking for chapter {chapter})")
		for key in keys:
			print(f"{key} {targetAssignments[key].name}")
		key=int(input(f"Enter the key for the assignment that {student.name}'s video should be recorded in:"))
		if not confirm(f"use {targetAssignments[key].name}?"):
			key=input(f"Enter the key for the assignment that {student.name}'s video should be recorded in:")
		chapter=targetAssignments[key].name.split("Ch ")[1].split(")")[0]
		c=[c for c in creationsWithContent if c.author_id == sourceSub.user_id][0]
		c.chapter=chapter
	targetAssignment=targetAssignments[key]
		
	targetSub=submissionByUA[student.id][targetAssignment.id]

	if dryrun:
		print(f"would post a grade of {sp} in {targetAssignment.name} for {student.name}")	
	else:
		print(f"Posting a grade of {sp} in {targetAssignment.name} for {student.name}")	
		targetSub.edit(submission={'posted_grade':sp})


if confirm(f"\nPublish the target assignments?"):
	#publish the assignments
	for key in targetAssignments:
		targetAssignments[key].edit(assignment={'published':True})

print("Here is what will get posted: ")
for s in students:
	updateGradebook(s, dryrun=True)

confirm("\nType ok when ready to upload student grades: ")
for s in students:
	updateGradebook(s, dryrun=False)

#confirm("Type ok when you have confirmed student grades on canvas ")

if confirm(f"Remove {sourceAssignment.name} source assignment from gradebook?"):
	sourceAssignment.edit(assignment={'grading_type':'not_graded'})

for group in scoreGroups:
	publishedAssignments=len([a for a in assignments if a.assignment_group_id == group.id and a.published])
	scoresToDrop=publishedAssignments-1
	if confirm(f"{group.name} has {publishedAssignments} published assignments.  Drop the lowest {scoresToDrop}?"):
		group.edit(rules={'drop_lowest': scoresToDrop})


print()
print(f"Done!")		