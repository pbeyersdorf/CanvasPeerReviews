#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()


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

#get the assignment target base name
assignmentBaseName=sourceAssignment.name
while not confirm(f"use {assignmentBaseName} as the target assignment base name?"):
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
		print(f"Creating a new assignment named {assignmentName} in group")
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
		print(f"Using existing assignment {targetAssignment.name}")
	getWorkInGroup(group)

def updateGradebook(student):
	#get the group that the student has the lowest score in
	scoreByGroupId=dict()
	lowestGroupScore=999999
	for group in scoreGroups: 
		if group.id not in scoreByGroupId:
			pass #scoreByGroupId[group.id]=-1
		for a in assignments:
			if a.assignment_group_id==group.id and submissionByUA[student.id][a.id].score!=None and (group.id not in scoreByGroupId or submissionByUA[student.id][a.id].score > scoreByGroupId[group.id]):
				scoreByGroupId[group.id]=submissionByUA[student.id][a.id].score
		if group.id in scoreByGroupId and scoreByGroupId[group.id]<lowestGroupScore:
			groupWithLowestScore=group
			lowestGroupScore=scoreByGroupId[group.id]
	
	#get the target assignment in this group
	targetAssignment=targetAssignments[groupWithLowestScore.id]
	targetSub=submissionByUA[student.id][targetAssignment.id]
	
	#get students grad on source assignment
	sourceSub=submissionByUA[student.id][sourceAssignment.id]
	sp=sourceSub.score
	if (sp>0 and confirm(f"Posting a grade of {sp} to {targetAssignment.name} for {s.name}")) :
		targetSub.edit(submission={'posted_grade':sp})

if confirm(f"Publish the target assignments?"):
	#publish the assignments
	for key in targetAssignments:
		targetAssignments[key].edit(assignment={'published':True})

confirm("Type ok when ready to upload student grades: ")
	
for s in students:
	updateGradebook(s)

#confirm("Type ok when you have confirmed student grades: ")

if confirm(f"Remove {sourceAssignment.name} source assignment from gradebook?"):
	sourceAssignment.edit(assignment={'grading_type':'not_graded'})

for group in scoreGroups:
	publishedAssignments=len([a for a in assignments if a.assignment_group_id == group.id and a.published])
	scoresToDrop=publishedAssignments-1
	if confirm(f"{group.name} has {publishedAssignments} published assignments.  Drop the lowest {scoresToDrop}?"):
		group.edit(rules={'drop_lowest': scoresToDrop})


print()
print(f"Done!")		