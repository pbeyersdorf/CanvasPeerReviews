#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
params.alternativeFeedbackTemplate="feedback_template_for_finals.txt" #this template doesn't have phrasing allowing regrades

print("If you don't want to allow regrades, make sure to modify the text of feedback_template.txt")

# if no assignments have yet been graded then prompt for graders
print("Not assigning any graders.  Uncomment the block below this to include graders.")
# if len([g for g in graded_assignments.values() if g.graded])==0: 
# 	assignGraders()
# else:
# 	viewGraders()
# 	val=inputWithTimeout("(g) update grader list",3)
# 	if (val=='g'):
# 		assignGraders()
#activeAssignment=lastAssignment
#if activeAssignment.graded:

while True:
	print("ctrl-c to end or:")
	activeAssignment=chooseAssignment(requireConfirmation=False, filter="Final")

	print("The following point distribution will be used for "+activeAssignment.name+":")
	for cid in activeAssignment.criteria_ids():
		multiplier=params.pointsForCid(cid, activeAssignment)
		print("\t" + str(multiplier)+ " points for '"+   criteriaDescription[cid] + "'")
	print("If this isn't ok, quit now and uncomment lines 31-36 in the script")
	# if not confirm():
	# 	setPoints(lastAssignment)
	# 	val=input("Enter any additional comments to post with the grades: ").strip()
	# 	if val!="":
	# 		utilities.additionalGradingComment=val+"\n\n"

	# Get creations and reviews
	getStudentWork(activeAssignment)

	
	print(activeAssignment.name + " is done with peer reviewing \nlet's make it the active assignment.")
	#val=inputWithTimeout("Will look for regrades from previous weeks.  (s) to skip",5)
	#if val!='s':
	#	regrade()
	#val=inputWithTimeout("Will calibrate student graders.  (s) to skip",5)
	#if val!='s':
	calibrate()

	#overrideDefaultPoints(activeAssignment)

	val=inputWithTimeout("using '" + activeAssignment.reviewCurve + "' for review scores.  (c) to change",2)
	if val=='c':
		activeAssignment.reviewCurve=confirm(msg="Enter curve as a function of rms: ", requireResponse=True)

	acceptedCurve=False
	while not acceptedCurve:
		curve=input(f'Enter an expression that takes a raw score x (out of {int(activeAssignment.points_possible)}) and returns a curved score, for instance "round({activeAssignment.points_possible/2}+x/2)": ')
		if curve=="":
			curve="x"
		activeAssignment.curve=curve
		grade(activeAssignment)	
		getStatistics(activeAssignment, hist=True)
		acceptedCurve=confirm("Are thes statistics ok?")
	log("Accepted " + activeAssignment.curve + " as the curve for " +  activeAssignment.name)

	print("\nGrades saved to file 'scores for " + activeAssignment.name + "'")
	exportGrades(activeAssignment)
	print("Grades exported")
	print()
	if confirm("Post grades on canvas?", False):
		postGrades(activeAssignment)
	print(f"Done grading {activeAssignment.name}")
	del(params.alternativeFeedbackTemplate)
	finish(True)
	params.alternativeFeedbackTemplate="feedback_template_to_finals.txt" #this template doesn't have phrasing allowing regrades
