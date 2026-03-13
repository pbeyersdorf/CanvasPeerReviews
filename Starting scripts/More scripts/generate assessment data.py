from path_info import *
from cpr import *		# the main module for managing peer reviews


COURSE_IDS=[COURSE_ID] # to assess multiple courses add the IDs in this list
for COURSE_ID in COURSE_IDS:
	#################  Get course info  #################
	students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)
	
	#################  Get relevant parameters assignment  #################
	params=getParameters()
	
	#get all student work
	getGradedAssignments(utilities.course)
	
	average={}
	success={}
	fail={}
	total={}
	successThreshold=3
	outputData=[]
	for aid in graded_assignments:
		ga=graded_assignments[aid]
		if aid != 'last' and ga.secondsPastDue()>0 and ga.published:
			print(f"Getting work on {ga.name}")
			#update the target scores in the database from Canvas
			submissions=ga.get_submissions()
			getStudentWork(ga)
			getReviews(creations)
		else:
			print(f"skipping {ga.name}")
	
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
			dataRow=[ga.due_at, ga.name]
			headerRow=["Due Date", "Assignment Name"]
			average[aid]=total
			print(f"For {graded_assignments[aid].name}:")
			for category in total:
				average[aid][category]=total[category]/count
				print(f"\t{category}: {average[aid][category]}, {round(success[category]*100/(success[category] +fail[category]))}% success rate")
				dataRow+=[ str(average[aid][category]), str(success[category]*100/(success[category] +fail[category]))]
				headerRow+=[category + ": Average", category+ ": Success Rate (%)"]
		
			if len(outputData)==0:
				outputData.append(headerRow)
			outputData.append(dataRow)
	
	courseName=utilities.course.name
	
	with open(courseName + ".tsv", "w") as file:
		for line in outputData:
			file.write(("\t".join(line))+"\n")