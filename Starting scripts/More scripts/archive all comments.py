#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
activeAssignment=lastAssignment
assignments = utilities.course.get_assignments()
now=datetime.utcnow().replace(tzinfo=pytz.UTC)
assignmentsToCheck=[]
filesToRemove=[]
commentsToProcess=[]

runWithArguments = len(sys.argv)>1

print('''
This will archive all instructor comments on all assignmetns.  
Run at the end of the semester to get an archive of comments that might
be useful to cut and paste as feedback in future semesters
''')	

for i,assignment in enumerate(assignments):
	try:
		if assignment.published and (now-assignment.due_at_date).total_seconds() >0:
			assignmentsToCheck.append(assignment)
	except:
		pass

def getCommentOnAssignment(assignment):
	if not assignment.published:
		print(f"{assignment.name} is not published - not looking for comments")
		return
	# Get creations and reviews
	submissions=assignment.get_submissions()
	printedResult=False
	commentsForThisAssignment=[]
	from html import escape
	
	for i,c in enumerate(submissions):
		print("\n" +assignment.name + ": Checking creation " + str(i) + "/" + str(len(students)), end="", flush=True)
		hideCursor()
		allCreationComments=c.edit().submission_comments
		for comment in allCreationComments:
			commentTime= datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
			thisDelta=datetime.utcnow()-commentTime
			delta=thisDelta.total_seconds() #age of comment in seconds
			previewUrl=c.preview_url.split("?")[0]
			speedGraderURL=previewUrl.replace("assignments/","gradebook/speed_grader?assignment_id=").replace("/submissions/", "&student_id=").replace("?version=1","")
			c.author_id=c.user_id
			if (comment['author']['id'] not in studentsById):
				print("\rYou said: \n" + Fore.BLUE +  Style.BRIGHT + comment['comment'] +  Style.RESET_ALL + "\n")
				commentsToProcess.append({'creation': c, 'comment': comment, 'assignment': assignment})
				commentsForThisAssignment.append(comment['comment'])
	fileName=status['dataDir'] + "instructor comments on " + assignment.name + ".txt"
	if len(commentsForThisAssignment)>0:
		f = open(fileName, "w")
		f.write("Instructor comments on " + assignment.name + "\n\n")
		textForFile="\n\n".join(list(set(commentsForThisAssignment)))
		f.write(textForFile)
		f.close()


for activeAssignment in assignmentsToCheck:
	print(f"\nChecking {activeAssignment.name} for comments:" )
	getCommentOnAssignment(activeAssignment)
showCursor()

