#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from CanvasPeerReviews import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
activeAssignment=lastAssignment
activeAssignment=chooseAssignment(requireConfirmation=False, timeout=3)

def getRecentCommentOnAssignment(assignment):
	# Get creations and reviews
	getStudentWork(assignment)

	print("\033[1m" + "Author comments on creations for " + assignment.name + "\033[0m")
	fileName=status['dataDir'] + assignment.name + "_comments.html"
	f = open(fileName, "w")
	f.write("<html><head><title>Author comments on " + assignment.name + " </title><style>\n")
	f.write("a {text-decoration:none}\n")
	f.write("</style><meta http-equiv='Content-Type' content='text/html; charset=utf-16'></head><body>\n")
	f.write("<h3>Author comments on "+assignment.name+"</h3>\n<table>\n")

	from html import escape
	commentsToProcess=[]
	for i,c in enumerate(creations):
		print("\rChecking creation " + str(i+1) + "/" + str(len(creations)), end="", flush=True)
		hideCursor()
		allCreationComments=c.edit().submission_comments
		for comment in allCreationComments:
			commentTime= datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
			thisDelta=datetime.utcnow()-commentTime
			delta=thisDelta.total_seconds() #age of comment in seconds
			previewUrl=c.preview_url.split("?")[0]
			speedGraderURL=previewUrl.replace("assignments/","gradebook/speed_grader?assignment_id=").replace("/submissions/", "&student_id=").replace("?version=1","")
			if (comment['author']['id'] == c.author_id):
				replied=False
				for otherComment in allCreationComments:
					otherCommentTime=datetime.strptime(otherComment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
					thisDelta=otherCommentTime-commentTime
					delta=thisDelta.total_seconds()
					if (delta>0 and otherComment['author']['id'] not in studentsById ):
						replied = True
				if not replied:
					printLine(msg="", newLine=False)
					print("\r"+comment['author']['display_name'] + " said: \n" + Fore.GREEN +  Style.BRIGHT + comment['comment'] +  Style.RESET_ALL + "\n")
					commentsToProcess.append({'creation': c, 'comment': comment})
					f.write("<tr><td>" + " <img src='" +comment['author']['avatar_image_url']+ "'><br>\n" + comment['author']['display_name'] +"</td>")
					f.write("<td> " + comment['author']['display_name'].split(" ")[0] + " said: <a href='"+ speedGraderURL +"'>" + escape(comment['comment']).replace("’","'") + "</a></td></tr>")
	f.write("</table></body></html>\n")
	f.close()
	if len(commentsToProcess)>0:
		subprocess.call(('open', fileName))

	showCursor()
	printLine(msg="", newLine=False)
	val=""
	for i,commentData in enumerate(commentsToProcess):
		printLine(line=True)
		comment=commentData['comment']
		c=commentData['creation']
		print(str(i+1) + "/" + str(len(commentsToProcess)) + "\t"+ comment['author']['display_name'] + " said: \n" + Fore.GREEN+  Style.BRIGHT + comment['comment'] +  Style.RESET_ALL)
		#print("\n" + Fore.MAGENTA +speedGraderURL + Style.RESET_ALL)
		proceed=False
		while not proceed:
			if val!='S':
				val=input("\n(c) to view context, (s) to skip, (S) to skip all or type a response:\n").strip()
			if val.lower()=="c":
				allCommentsForThisSubmission=c.edit().submission_comments
				for thisComment in allCommentsForThisSubmission:
					if thisComment['author']['id'] not in studentsById:
						color=Fore.BLUE +  Style.BRIGHT
					else:
						if (thisComment['author']['id'] == c.author_id):
							color=Fore.GREEN +  Style.BRIGHT
						else:
							color=Fore.MAGENTA +  Style.BRIGHT
					print("\n\n" + thisComment['author']['display_name']+ " said:\n"+ color + thisComment['comment'] + Style.RESET_ALL)
			elif val.lower()=="s" or val=="":
				print("Skipping")
				proceed=True
			else:
				print("Posting comment...")
				c.edit(comment={'text_comment':val})
				proceed=True
printLine(line=True)
getRecentCommentOnAssignment(activeAssignment)
print("\nactiveAssignment=chooseAssignment()\ngetRecentCommentOnAssignment(activeAssignment)\n\nto get comments on an earlier assignment")

