#################  Set up where to the environment  #################
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
#################  Get relevant parameters assignment  #################
params=getParameters()

n=int(getNum("How many of the lowest assignmetns should we find? "))
useDB=confirm("Shall we use the internal database?  It is faster than looking grades up on canvas, but may be inacurate: ")
# print n lowest assignments
if not useDB:
	studentScores=dict()
	for s in students:
		studentScores[s.id]=dict()
	for num in assignmentByNumber:
		a=assignmentByNumber[num]
		if a.published:
			print("getting submission from " +  a.name)
			submissions=a.get_submissions()
			for creation in submissions:
				creation.author_id=creation.user_id
				if creation.author_id in studentsById:
					if creation.score !=None:
						studentScores[creation.author_id][a.name]=creation.score

		

val=""
tally=dict()
msg=""
for key in graded_assignments:
	ga=graded_assignments[key]
	tally[ga.name]=0

#studentsIn3=[s for s in students if "03" in s.sectionName]
for s in students:
	msg+="\n"+s.name+","
	if s.role=="student":
		try:
			if useDB:
				grades=[{'grade': s.grades[key]['curvedTotal'], 'key': key} for key in s.grades]
				grades.sort(key=lambda x: x['grade'])
				lowest=[graded_assignments[grades[i]['key']].name for i in range(n)]
			else:
				grades=[{'grade': studentScores[s.id][key], 'key': key} for key in studentScores[s.id]]
				grades.sort(key=lambda x: x['grade'])
				lowest=[grades[i]['key'] for i in range(n)]
			lowestScores=[grades[i]['grade'] for i in range(n)]
			#lowestNumbers=sorted([int(''.join(list(filter(str.isdigit,aname)))) for aname in lowest])
			print(s.name, lowest)
			for name in lowest:
				tally[name]+=1
			try:
				completedBonusAssignment=s.grades[6387969]['curvedTotal']>0
			except:
				completedBonusAssignment=False
			if completedBonusAssignment:
				body=f"Hi {s.name.split(' ')[0]}, I just wanted to let you know that as of now (before the chapter 16 quiz) your two lowest quiz scores are from {lowest[0].replace(' in-class quiz','')} ({lowestScores[0]}) and {lowest[1].replace(' in-class quiz','')} ({lowestScores[1]}).  If you score above {max(lowestScores)} on the chpater 16 quiz, then these will be the two quizzes that you retake during the final exam period, otherwise you would retake {lowest[0].replace(' in-class quiz','')} and Ch 16.  If (and only if) you improve your scores on the retakes, will your original scores be replaced, so your grade can only be improved from these retakes.  Once your original scores have been updated your lowest remaining score will be dropped (since you completed the bonus video assignment) and your grade on the bonus video assignment will be used in its place to calcualte your grade.  This will all be reflected on canvas.   Let me know if you have any quesitons."
			else:
				body=f"Hi {s.name.split(' ')[0]}, I just wanted to let you know that as of now (before the chapter 16 quiz) your two lowest quiz scores are from {lowest[0].replace(' in-class quiz','')} ({lowestScores[0]}) and {lowest[1].replace(' in-class quiz','')} ({lowestScores[1]}).  If you score above {max(lowestScores)} on the chpater 16 quiz, then these will be the two quizzes that you retake during the final exam period, otherwise you would retake {lowest[0].replace(' in-class quiz','')} and Ch 16.  If (and only if) you improve your scores on the retakes, will your original scores be replaced, so your grade can only be improved from these retakes.  Let me know if you have any quesitons."
			print()
			print()
			print(body)
			print()
			print()
			if val.lower()==val:
				val = input("(y)to send message to " + s.name + ", (Y) to stop asking and send to all ")
			if val.lower()=="y":
				message(s, body, subject='final quiz retake information', display=True)
			if int(''.join(list(filter(str.isdigit,lowest[0]))))<int(''.join(list(filter(str.isdigit,lowest[1])))):
				s.temp=(f"{s.name}: {lowest[0].replace(' in-class quiz','')} and {lowest[1].replace(' in-class quiz','')}")
			else:
				s.temp=(f"{s.name}: {lowest[1].replace(' in-class quiz','')} and {lowest[0].replace(' in-class quiz','')}")
# 			for key in graded_assignments:
# 				ga=graded_assignments[key]
# 				if ga.name in lowest:
# 					msg+=f"{ga.name},"
# 				else:
# 					msg+=","
		except Exception:
			print("Error processing "+ s.name)
	
print("Here are the retake counts")
for name in tally:
	print(tally[name],"retakes of ", name)

print("For section 5:")
for s in students:
	if "05" in s.sectionName:
		try:
			print(s.temp)
		except:
			pass
	
print("For section 3:")
for s in students:
	if "03" in s.sectionName:
		try:
			print(s.temp)
		except:
			pass
			
#print(msg)