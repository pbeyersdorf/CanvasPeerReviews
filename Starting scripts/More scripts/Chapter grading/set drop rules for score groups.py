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

for group in scoreGroups:
	publishedAssignments=len([a for a in assignments if a.assignment_group_id == group.id and a.published])
	scoresToDrop=publishedAssignments-1
	if confirm(f"{group.name} has {publishedAssignments} published assignments.  Drop the lowest {scoresToDrop}?"):
		group.edit(rules={'drop_lowest': scoresToDrop})

print()
print(f"Done!")