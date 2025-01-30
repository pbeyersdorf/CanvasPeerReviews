#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

#from datetime import datetime
#import pytz

course=utilities.course
groups=course.get_assignment_groups()
#for groups like "ch 6 work", "ch 6 tests", "ch 6 grade" the possible suffixes:
sufixes={'score': 'score'}

print('''
This script will create an assignment in every scoring group. 
If the base name of the assignment is "Extra Credit" then it will
create an assignment in the "Ch 5 score" group called 
"Extra Credit (Ch 5)" and so on for every scoring group.

This is useful to report grades for an assignment that is not specific
to one particular chapter, but you want to allow the students to use
it to replace the score for a particular chapter.
''')

#get the assignment name and details here
assignmentBaseName=input("Enter assignment base name: ")


scoreGroups=[g for g in groups if sufixes['score'] in g.name]
for group in scoreGroups:
	core=group.name.replace(sufixes['score'],"").strip()
	assignmentName=assignmentBaseName + " (" + core +")"
	print(assignmentName)
	
	print(f"Creating a new assignment named {assignmentName} in group")
	course.create_assignment({
	'name': assignmentName,
	'points_possible': 100,
	'due_at': datetime.now(),
	'description': "Score for the '" + assignmentBaseName +"' assignment applied to " + core,
	'published': False,
	'assignment_group_id': group.id
	}) 


printLine("Done! make sure to check the gradebook ",newLine=False)