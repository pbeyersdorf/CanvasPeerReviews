#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
print("Syncing all work, reviews and assignments that are past due.")

for s in students:
	s.comparisons=dict()

for key in graded_assignments:
	ga=graded_assignments[key]
	if key != 'last' and ga.secondsPastDue()>0 and ga.published and ga.graded:
		print(f"Getting work on {ga.name}")
		#update the target scores in the database from Canvas
		submissions=ga.get_submissions()
		for creation in submissions:
			creation.author_id=creation.user_id
			if creation.author_id in studentsById:
				if creation.score !=None:
					studentsById[creation.author_id].grades[ga.id]['curvedTotal']=creation.score
utilities.dataToSave['students']=True
finish(True)

