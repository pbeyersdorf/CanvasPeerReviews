from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get course info  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

#################  Get relevant parameters assignment  #################
params=getParameters()

average={}
success={}
fail={}
total={}
successThreshold=3
for aid in graded_assignments:
	theseReviews=[reviewsById[key] for key in reviewsById if reviewsById[key].assignment_id == aid]
	count=0
	for thisReview in theseReviews:
		completeAndWithinLimits=True
		for category in total:
			try:
				if thisReview.scores[category] >4:
					completeAndWithinLimits=False
			except:
				completeAndWithinLimits=False
		if not completeAndWithinLimits:
			continue
		if count ==0:
			for category in thisReview.scores:
				total[category]=thisReview.scores[category]
				if (thisReview.scores[category] >=successThreshold):
					success[category]=1
					fail[category]=0
				else:
					success[category]=0
					fail[category]=1				
				total[category]=thisReview.scores[category]
				total[category]=thisReview.scores[category]
		else:			
			for category in total:
				total[category]+=thisReview.scores[category]
				if (thisReview.scores[category] >=successThreshold):
					success[category]+=1
				else:
					fail[category]+=1				

		count+=1

	if count>0:
		average[aid]=total
		for category in total:
			average[aid][category]=total[category]/count
		print(f"For {graded_assignments[aid].name}:")
	
		for category in average[aid]:
			print(f"\t{category}: {average[aid][category]}, {round(success[category]*100/(success[category] +fail[category]))}% success rate")
	
		