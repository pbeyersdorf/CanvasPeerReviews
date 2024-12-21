from jinja2 import Environment, select_autoescape, FileSystemLoader

def writeTemplate(fileName="feedback_template.txt"):
	from importlib import resources as impresources
	from . import templates
	inp_file = impresources.files(templates) / 'feedback_template.txt'
	with inp_file.open("rt") as f:
		template = f.read()
	f = open(fileName, "w")
	f.write(template)
	f.close()
	print(f"Writing new template to  {fileName}")
	return template

######################################
# fill out student grade information using a template to format it
def processTemplate(student, assignment, templateName):
	global params
	if assignment.id not in student.creations:
		return None
	env = Environment(loader=FileSystemLoader('templates'))
	if not  hasattr(student,"pointsByCriteriaScaled"):
		student.pointsByCriteriaScaled=dict()
	if assignment.id not in student.pointsByCriteriaScaled:
		student.pointsByCriteriaScaled[assignment.id]=dict()
	try:
		for cid in assignment.criteria_ids(): 
			student.pointsByCriteriaScaled[assignment.id][cid]=0
			try:
				if cid in student.pointsByCriteria[assignment.id]:
					if student.pointsByCriteria[assignment.id][cid]!='':
						student.pointsByCriteriaScaled[assignment.id][cid]=round(student.pointsByCriteria[assignment.id][cid] * assignment.criteria_points(cid)/ params.pointsForCid(cid, assignment),2)				
			except:
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
			pointsByCriteria=student.pointsByCriteriaScaled
		else:
			creationGrade=creationPoints=reviewGrade=rawGrade=curvedGrade=curvedPoints=reviewPoints=rawPoints="--"
		
	except KeyError:
		print("Key error for " + student.name + " perhaps they dropped")
		return ""

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
 		pointsByCriteria=student.pointsByCriteriaScaled[assignment.id],
 		criteria_description=criteriaDescription,
 		student=student,
 		assignment=assignment
 		)
	return renderedTemplate

print("The PATH OF THE CURRENT MODULE IS=", end=.__file__)