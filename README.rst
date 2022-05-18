Installation
python -m pip install -e path/to/CanvasPeerReviews

Usage:
from CanvasPeerReviews import *
initialize()
lastAssignment=graded_assignments['last']
getParameters()
getStudentWork()

if (lastAssignment.countPeerReviews()==0):
	assignCalibrationReviews() #look for any submissions that have been graded and assign those as peer reviews to all students				
	assignPeerReviews(creations, numberOfReviewers=params.numberOfReviews)	
elif peerReviewingOver(lastAssignment):
	calibrate() # update students grading power based on how well their reviews aligned to everyone else
	grade(lastAssignment)				
	exportGrades(lastAssignment, display=True)
	if confirm("Post grades on canvas?", False):
		postGrades(lastAssignment)
