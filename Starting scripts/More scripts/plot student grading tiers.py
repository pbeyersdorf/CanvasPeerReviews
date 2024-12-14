#################  Set up where to the environment  #################
from path_info import * 			# Set up where to find the relevant files
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()
# if no assignments have yet been graded then prompt for graders

# ######This is only necessary when rebuilding the data
# for s in students:
# 	s.submissionsCalibratedAgainst=dict()
# 	s.adjustmentsByAssignment=dict()
# 	s._dataByAssignment=dict()
# calibrate()
# #######


import matplotlib.pyplot as plt
val=None
gas=[graded_assignments[key] for key in graded_assignments if graded_assignments[key].graded and key != 'last']
sortefAssignments = sorted(gas, key=lambda x:x.date)
while val != 'done':
	val=input("Enter the name (or partial name) of the student to inspect: ")
	s=selectStudentByName(val)
	msg=""
	cid=0
	x=[]
	y1=[]
	y2=[]
	y3=[]
	y4=[]
	i=0
	for ga in sortefAssignments:
		if ga.graded:
			try:
				i+=1
				y1temp=s.getGradingPowerByAssignment(ga.id, cid)
				y2temp=s.adjustmentsByAssignment[ga.id][cid].gradingPower(normalizationFactor="auto")
				if ga.id==6272806:
					xtemp="Ch 10.2"						
				else:
					xtemp=" ".join(ga.name.split(" ")[:2])
				upperTier=np.percentile([s.adjustmentsByAssignment[ga.id][cid].gradingPower(normalizationFactor="auto") for s in students],66.66)
				lowerTier=np.percentile([s.adjustmentsByAssignment[ga.id][cid].gradingPower(normalizationFactor="auto") for s in students],33.33)
				success=y1temp != None
			except:
				msg=(f"{s.name} has no data for {ga.name}")
				success=False
			if success:
				y1.append(y1temp)
				y2.append(y2temp)
				y3.append(lowerTier)
				y4.append(upperTier)
				x.append(xtemp)
	plt.scatter(x, y1)
	plt.plot(x, y2, label = 'accumulated total')
	plt.plot(x, y3, label = '33 percentile')
	plt.plot(x, y4, label = '67 percentile')
	plt.legend()
	plt.title('rms data for ' + s.name)
	if msg!="":
		print(msg)
	plt.show()

			
			
