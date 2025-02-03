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
while val != 'done':
	val=input("Enter the name (or partial name) of the student to inspect: ")
	if val.strip().lower()!="all":
		s=selectStudentByName(val)
		y1=dict()
		y2=dict()
		try:
			x=[]
			y1=[]
			y2=[]
			y3=[]
			i=0
			for key in graded_assignments:
				ga=graded_assignments[key]
				if ga.graded:
					i+=1
					if ga.id in s.grades:
						if ga.id==6272806:
							x.append("Ch 10.2")						
						else:
							x.append(" ".join(ga.name.split(" ")[:2]))
						y1.append(s.grades[ga.id]['review'])
						y2.append(s.grades[ga.id]['creation'])
						y3.append(s.grades[ga.id]['curvedTotal'])
			plt.scatter(x, y1)
			plt.plot(x, y1, label = "review")
			plt.scatter(x, y2)
			plt.plot(x, y2, label = "creation")
			plt.scatter(x, y3)
			plt.plot(x, y3, label = "total")
			plt.legend()
			plt.title('scores for ' + s.name)
			plt.ylim(0,100)
			plt.show()
		except TypeError:
			print("unable to plot data for " + s.name)
	else:
		cid=0
		y1=dict()
		y2=dict()
		y3=dict()
		for s in students:
			try:
				i=0
				x=[]
				y1[s.id]=[]
				y2[s.id]=[]
				y3[s.id]=[]
				for key in graded_assignments:
					ga=graded_assignments[key]
					if ga.graded:
						i+=1
						if ga.id in s.grades:
							if ga.id==6272806:
								x.append("Ch 10.2")						
							else:
								x.append(" ".join(ga.name.split(" ")[:2]))
							y1[s.id].append(s.grades[ga.id]['review'])
							y2[s.id].append(s.grades[ga.id]['creation'])
							y3[s.id].append(s.grades[ga.id]['total'])
				plt.plot(x, y3[s.id], label = s.name)
			except KeyError:
				pass
		#plt.legend()
		plt.title('grades for all students')
		plt.show()
			
			
