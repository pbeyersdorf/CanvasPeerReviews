#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get course info  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

s=students[0]
cid='_2681'
print(s.name, criteriaDescription[cid], params.weeklyDegradationFactor())

print("This is columns B-D in the spreadhseet")
for num in [5,6,7,8,9,10,102,11,12,13,14]:
	ga=assignmentByNumber[num]
	s.updateAdjustments(normalize=True, weeklyDegradationFactor=params.weeklyDegradationFactor(), upToAssignment=ga.id)
	adj=s._dataByAssignment[ga.id][cid]
	print(ga.name, adj.delta, adj.delta2, adj.weight, round(adj.delta/adj.weight,2), round((adj.delta2/adj.weight)**0.5,2), 
	round(params.weeklyDegradationFactor(),2),s.adjustments[cid].compensation,
	round(s.adjustments[cid].rms,2), round(s.adjustments[cid].gradingPower,2),
	round(s.adjustments[cid].weight,2))

