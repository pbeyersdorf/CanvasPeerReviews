#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
activeAssignment=chooseAssignment(requireConfirmation=False,  timeout=5, defaultAssignment=lastAssignment)


# Get creations and reviews
getStudentWork(activeAssignment)

print("\033[1m" + "Looking at comments for " + activeAssignment.name + "\033[0m")

commentsToProcess=[]
allComments=[]
commentTarget=dict()
commentCreation=dict()
for i,c in enumerate(creations):
	print("\rChecking creation " + str(i+1) + "/" + str(len(creations)), end="", flush=True)
	hideCursor()
	creationComments=c.edit().submission_comments
	for comment in creationComments:
		commentTarget[comment['id']]=c.author.name
		commentCreation[comment['id']]=c
	allComments+=creationComments
showCursor()
commentAuthors=dict()
for comment in allComments:
	commentAuthors[comment['author']['id']]=comment['author']['display_name']
instructorName=[commentAuthors[key] for key in commentAuthors if key not in studentsById][0]
commenter=instructorName
print("\nOK...will look at comments by " + commenter)
commentsByCommenter=[comment for comment in allComments if comment['author']['display_name'] == commenter]

howManyMinutesBack=float(input("Consider comments that were made in the past how many minutes? "))
now=datetime.now()
offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
val=''
for comment in commentsByCommenter:
	target=commentTarget[comment['id']]
	commentTime= datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
	minutesSinceComment=((now-commentTime).total_seconds()+ offset)/60
	if minutesSinceComment< howManyMinutesBack:
		printLine(line=True)
		if (val!='D' and val!='S'):
			print(comment['comment'])
			print("\nwas made to " +target+ " about " + str(round(minutesSinceComment)) + " minutes ago: ")
			val=input("\t(d) to delete this\n\t(D) to delete all\n\t(S) to skip all\n\t(s) or <enter> to skip this\nWhat is your choice?: ").strip()
		if (val.lower()=='d'):
			print("Deleting comment to " + target)
			c=commentCreation[comment['id']]
			# there isn't an interface through the python canvasapi module, so I had to use lower level code
			c._requester.request("DELETE",
            	"courses/{}/assignments/{}/submissions/{}/comments/{}".format(
                c.course_id, c.assignment_id, c.user_id, comment['id']
            )
        )
val=''
print("Done!")
		
	

