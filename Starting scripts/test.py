#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews
#from gitHub
#################  Get course info  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()


from jinja2 import Environment, select_autoescape, FileSystemLoader

def processTemplate(student, assignment, templateName):
	student=copy.deepcopy(student)
	global params, criteriaDescription
	if not os.path.isfile(f"{status['dataDir']}templates/macros.txt"):
		createTemplate(templateName="macros", showAfterCreate=False)
	if not os.path.isfile(f"{status['dataDir']}templates/{templateName}.txt"):
		createTemplate(templateName=templateName)
		print("Please edit the template and save it.")
	env = Environment(loader=FileSystemLoader(f"{status['dataDir']}templates"))
	if student==None:
		creationGrade=None
		creationPoints=None
		reviewGrade=None
		rawGrade=None
		curvedGrade=None
		curvedPoints=None
		reviewPoints=None
		rawPoints=None
		pointsByCriteria={}
		criteriaDescription={}
	else:
		if assignment.id not in student.creations:
			return None
		if not  hasattr(student,"pointsByCriteriaScaled"):
			student.pointsByCriteriaScaled=dict()
		if assignment.id not in student.pointsByCriteriaScaled:
			student.pointsByCriteriaScaled[assignment.id]=dict()
		try:
			for cid in assignment.criteria_ids(): 
				if cid not in student.deviationByAssignment[assignment.id]:
					student.deviationByAssignment[assignment.id][cid]=999
					student.rmsByAssignment[assignment.id][cid]=999
				student.pointsByCriteriaScaled[assignment.id][cid]=0
				if True:#try:
					if cid in student.pointsByCriteria[assignment.id]:
						if student.pointsByCriteria[assignment.id][cid]!='':
							student.pointsByCriteriaScaled[assignment.id][cid]=round(student.pointsByCriteria[assignment.id][cid] * assignment.criteria_points(cid)/ params.pointsForCid(cid, assignment),2)				
				else:#except:
					pass
			
			if assignment.id in student.grades:
				creationGrade=round(student.grades[assignment.id]['creation'])
				creationPoints=student.points[assignment.id]['curvedCreation']
				reviewGrade=round(student.grades[assignment.id]['review'])
				rawGrade=round(student.grades[assignment.id]['total'])
				curvedGrade=round(student.grades[assignment.id]['curvedTotal'])
				curvedPoints=student.points[assignment.id]['curvedTotal']
				reviewPoints=student.points[assignment.id]['review']
				rawPoints=student.points[assignment.id]['total']
				pointsByCriteria=student.pointsByCriteriaScaled[assignment.id]
			else:
				creationGrade=creationPoints=reviewGrade=rawGrade=curvedGrade=curvedPoints=reviewPoints=rawPoints="--"
			
		except KeyError:
			print("Key error for " + student.name + " perhaps they dropped")
			return ""
		
	if True:#try:
		renderedTemplate = env.get_template(templateName+'.txt').render(
			keywordCreation="regrade",
			keywordReview="recalculate",
			solutionsUrl=assignment.solutionsUrl,
			assignmentName=assignment.name,
			creationGrade=creationGrade,
			creationPoints=creationPoints,
			reviewGrade=reviewGrade,
			rawGrade=rawGrade,
			curvedGrade=curvedGrade,
			curvedPoints=curvedPoints,
			reviewPoints=reviewPoints,
			rawPoints=rawPoints,
			pointsByCriteria=pointsByCriteria,
			criteriaDescription=criteriaDescription,
			student=student,
			assignment=assignment
			)
	return renderedTemplate
	try:
		pass
	except KeyboardInterrupt:
		exit()
	except:
		print(f"Unable to render template for {student.name} - perhaps they dropped")
		return ""
	return renderedTemplate

assignment=graded_assignments[7251350]
student=students[0]
assignment.reviewDueDateString = "Friday, February 14 at midnight"

print(processTemplate(student, assignment, "peer review assignment description"))