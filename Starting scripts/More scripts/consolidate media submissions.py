#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
# if no assignments have yet been graded then prompt for graders

import requests, os, re, random
downloadContent=True
getPermissions=False

#helper function to find the first floating point number in a text string and return it as a float.
def getFirstFloatFromString(string):
	try:
		pattern=re.compile('[0-9]+[.][0-9]+')
		result=pattern.search(string)
		val=float(string[result.span()[0]:result.span()[1]])
		return val
	except:
		return 999
		
#default settings for permissions
okToShareNow=dict()
okToShareLater=dict()
attribute=dict()
for s in students:
	okToShareNow[s.id] = False
	okToShareLater[s.id]= False
	attribute[s.id]= False


################ get permission information
if getPermissions:
	assignments = utilities.course.get_assignments()
	a=[a for a in assignments if a.name=="Permission to use instructional video"][0]
	responses=a.get_submissions()
	
	for r in responses:
		if r.grade != None:
			okToShareNow[r.user_id] = int(r.grade) in [1,3,5,7]
			okToShareLater[r.user_id] = int(r.grade) in [2,3,6,7]
			attribute[r.user_id] = int(r.grade) in [4,5,6,7]

##################  Figure out the filename based on the comments 
a=chooseAssignment(requireConfirmation=False)
getStudentWork(a)
creationsWithContent=[c for c in creations if c.attempt != None]
if downloadContent:
	os.system('mkdir Downloads')
allFileNames=[]
urls=dict()
attributedTo=dict()
userIdByFilename=dict()
startingSlideByFileName=dict()
authorsWithoutComments=[]

for c in creationsWithContent:
	try:
		url=c.media_comment['url']
		downloadable=True
	except:
		url=c.url
		downloadable=False
	allCreationComments=c.edit().submission_comments
	authorComments=[]
	description=""
	defaultFileName=studentsById[c.user_id].name.title()
	filename=defaultFileName
	for comment in allCreationComments:
		cmnt=comment['comment']
		start=0
		end=0
		try:
			if comment['author_id'] == c.user_id and "(" in cmnt and ")" in cmnt:
				start=re.findall("\d+\.\d+",cmnt.split("(")[0])[0]
				topic=cmnt.split("(")[1].split(")")[0]
				authorComments.append(cmnt)
				filename="slides "+start + " (" + topic + ")"
			if comment['author_id'] == c.user_id and "-" in cmnt and "(" in cmnt and ")" in cmnt:
				start=re.findall("\d+\.\d+",cmnt.split("-")[0])[0]
				end=re.findall("\d+\.\d+",cmnt.split("-")[1])[0]
				topic=cmnt.split("(")[1].split(")")[0]
				authorComments.append(cmnt)
				filename="slides "+start + "-" + end + " (" + topic + ")"
		except:
			if comment['author_id'] == c.user_id and "(" in cmnt and ")" in cmnt:
				filename=cmnt
				try:
					start=float(cmnt.split("-")[0])
				except:
					pass
				if start==0:
					try:
						start=float(cmnt.split("(")[0])
					except:
						pass
			else:
				filename=studentsById[c.user_id ].name

	#### the following are manual overrides
	if filename == "ch7 11-13(electrical potential)":
		filename="slides 7.11-7.13 (electrical potential)"
	if filename == "Antonio Valdez":
		filename="slides 9.8-9.10 (Ohm's law)"
	if filename == "Hemanth Karnati":
		filename="slides 7.18-7.19 (Potential from a line charge)"
	if filename == "Ismet Gurleroglu":
		filename="slides 6.32 (line Charge Example)"
	if filename == "Joal Pena":
		filename="slides 7.4-7.8 (electric potential eenrgy)"
	if filename == "Khanh Nguyen":
		filename="slides 7.18-7.19 (potential from a charged rod)"
	if filename == "Naqeeb Hussain":
		filename="slides 7.25-7.26 (potential across chaerged plates)"
	if filename == "Sarah Xia":
		filename="slides 6.22-6.23 (electric flux)"
	if filename == "Steven Wise":
		filename="slide 5.34 (electric field of a line charge)"
	if filename == "Victor Spiessens":
		filename="slides 7.32-7.34 (field from potenetial)"	
	if filename == "Isabella Daza":
		filename="slides 7.25-7.26 (potential across charged plates)"
	if filename == "Udayveer Grewal":
		filename="slide 9.35 (power in circuits)"
	if filename == "Janet Vo":
		filename="slide 10.28 (RC circuit example)"
	if filename == "Fabiola Castillo":
		filename="slide 9.31-9.36 (Light bulbs in series and parallel)"		
	if filename == "Evan Peterson":
		filename="slides 7.18-7.19 (potential from a charged rod)"
	if filename == "Aarya Patil":
		filename="slide 10.29 (RC circuit example)"
	if filename == "Tyler Dunning":
		filename="slides 7.18 (Potential From a Rod of Charge)"
	if filename == "Jiaming Feng":
		filename="Jiaming Feng"
	if filename == "Ty Seligman":
		filename="slides 10.11-10.16 (Kirchoff's rules)"
	if filename == "Michael Rumawas":
		filename="slides 10.13-10.16 (Kirchoff's rules)"
	if filename == "Giorgios Koutantos":
		filename="slides 8.5-8.8 (Combining Capacitors)"
	if filename == "Diego Robles":
		filename="slides 7.25-7.26 (potential across charged plates)"
	if filename == "Kevin Tran":
		filename="slides 12.28-12.30 (Ampere's law)"
	if filename == "Jiaming Feng":
		filename="slides 7.19-7.24 (Potential from a charged sphere)"
	if filename == "Emmanuel Arellano - Haro":
		filename="slides 7.18 (potential from a rod of charge)"
		
	
########### Process the various files
	###make sure teh filename is title case and unique	
	filename=filename.title()
	start=getFirstFloatFromString(filename)
	originalFileName=filename
	if filename in allFileNames:
		i=2
		filename=originalFileName + " " +str(i)
		while originalFileName + " " +str(i) in allFileNames:
			i+=1
			filename=originalFileName + " " +str(i)
		print(f"updated {originalFileName} to be called {filename}")
	allFileNames.append(filename) 
	
	#record the location of the file and the author keyed to the name of the file
	urls[filename]=url
	userIdByFilename[filename]=c.user_id
	#create a string to attribute the video to the author if they have requested that
	if c.user_id in attribute and attribute[c.user_id]:
		attributedTo[filename]=" by " + studentsById[c.user_id].name
	else:
		attributedTo[filename]=""
	# capture the starting slide number for sorting later on
	startingSlideByFileName[filename]=start
	
	# make a list of all students whose topic and startign slides are unknown
	if filename == defaultFileName:
		authorsWithoutComments.append(studentsById[c.user_id])
	
	#download the video into a folder
#	if downloadContent and downloadable and okToShareLater[c.user_id]:
	if downloadContent and downloadable:
		response = requests.get(url)
		webpage = response.content
		print(f"downloading {filename}")
		with open('Downloads/' + filename.replace('/', '-') +  attributedTo[filename]+ ".mp4", "wb") as binary_file:
			binary_file.write(webpage)

##################  make a web page  ###########
htmlContent="<ul>\n"
sortedEntries = sorted(startingSlideByFileName.items(), key=lambda x:x[1])
for (filename,start) in sortedEntries:
	#if okToShareNow[userIdByFilename[filename]]:
	if True:
		htmlContent+="<li><a href='" + urls[filename] +"'>" +   filename + "</a>"+ attributedTo[filename]+"\n"
# 	else:
# 		htmlContent+="<li>" + filename + " " + attributedTo[filename]+"\n"		
htmlContent+="</ul>"
print(htmlContent)

print("")
n=3
print("The following students may not have covered a chapter that was among their lowest " +str(n)+" quiz scores:")
for (filename,start) in sortedEntries:
	try:
		s=studentsById[userIdByFilename[filename]]
		chapter=int(str(start).split(".")[0])
		grades=[{'grade': s.grades[key]['curvedTotal'], 'key': key} for key in s.grades]
		grades.sort(key=lambda x: x['grade'])
		for i in range(n):
			lowest=[graded_assignments[grades[i]['key']].name for i in range(n)]
			lowestNumbers=sorted([int(''.join(list(filter(str.isdigit,aname)))) for aname in lowest])
		if not chapter in lowestNumbers:
			print(s.name,int(str(start).split(".")[0]), lowestNumbers)
	except:
		pass



##################  offer to send a message to students whose filenames couldn't be determined 
if len(authorsWithoutComments)>0:
	print("Students without comments on their submissions:")
	for s in authorsWithoutComments:
		print("\t" + s.name)
	msg="Thanks for submitting a video.  Can you please add a comment to the submission indicating the slide numbers and topic of the video in the format x.xx-x.xx (topic).  For example if your video covered slides 6.33-6.34 on charges in conductors you would enter '6.33-6.34 (charges in conductors)'.  Thanks!"
	print("You can copyand paste the following if you wish:\n\n" + msg)
	val=input("\n\nType a message to send to some or all of these students or hit <enter> for the default message above, or (s) to skip:\n").strip()
	if val!="s":
		if val!="":
			msg=val
		for s in authorsWithoutComments:
			c=[c for c in creationsWithContent if c.user_id==s.id][0]
			allCreationComments=c.edit().submission_comments
			if len(allCreationComments)>0:
				print("\n\nComments for " + studentsById[c.user_id].name+ "\n")
				for comment in allCreationComments:
					cmnt=comment['comment']
					if comment['author_id'] == c.user_id:
						color=Fore.GREEN +  Style.BRIGHT
					else:
						color=Fore.BLUE +  Style.BRIGHT
					print("\n\n" + color + cmnt + Style.RESET_ALL)	
			if confirm("Post comment to " + s.name):
				print("Posting comment...")
				print(studentsById[c.user_id])
				c.edit(comment={'text_comment':val})
	