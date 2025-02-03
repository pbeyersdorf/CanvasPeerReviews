#################  Set up where to the environment  #################
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
	if val.strip().lower()!="all":
		s=selectStudentByName(val)
		y1=dict()
		y2=dict()
		msg=""
		for cid in list(s.criteriaDescription) + [0]:
			x=[]
			y1[cid]=[]
			y2[cid]=[]
			i=0
			#s.adjustmentsByAssignment=dict()
			#s.updateAdjustments(normalize=True, weeklyDegradationFactor=0.84)
			for ga in sortefAssignments:
				if ga.graded:
					try:
						i+=1
						#y1.append(s._dataByAssignment[ga.id][cid].rms())
						#y2.append(s.adjustmentsByAssignment[ga.id][cid].rms)
						#y1[cid].append(s._dataByAssignment[ga.id][cid].rms())
						y1temp=s.rmsByAssignment[ga.id][cid]
						#y2[cid].append(s.adjustmentsByAssignment[ga.id][cid].rms)
						y2temp=s.adjustmentsByAssignment[ga.id][cid].rms
						#x.append(i)
						if ga.id==6272806:
							xtemp="Ch 10.2"						
						else:
							xtemp=" ".join(ga.name.split(" ")[:2])
						success=y1temp!=None
					except:
						msg=(f"{s.name} has no data for {ga.name}")
						success=False
					if success:
						y1[cid].append(y1temp)
						y2[cid].append(y2temp)
						x.append(xtemp)
						
			#plt.plot(x, y1, label = "data")
			#plt.plot(x, y2, label = "adjustments")
			plt.scatter(x, y1[cid])
			if cid!=0:
				plt.plot(x, y2[cid], label = criteriaDescription[cid])
			else:
				plt.plot(x, y2[cid], label = 'accumulated total')
		plt.legend()
		plt.title('rms data for ' + s.name)
		if msg!="":
			print(msg)
		plt.show()
	else:
		cid=0
		y=dict()
		for s in students:
			try:
				i=0
				x=[]
				y[s.id]=[]
				s.adjustmentsByAssignment=dict()
				s.updateAdjustments(normalize=True, weeklyDegradationFactor=params.weeklyDegradationFactor())
				for key in graded_assignments:
					ga=graded_assignments[key]
					if ga.graded:
						i+=1
						#x.append(i)
						if ga.id==6272806:
							x.append("Ch 10.2")						
						else:
							x.append(" ".join(ga.name.split(" ")[:2]))
						y[s.id].append(s.adjustmentsByAssignment[ga.id][cid].gradingPower)
				plt.plot(x, y[s.id], label = s.name)
			except KeyError:
				pass
		#plt.legend()
		plt.title('total grading power for all students')
		plt.show()
			
			
