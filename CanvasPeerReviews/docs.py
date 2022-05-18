print("cprhelp() for information")
def cprhelp(subject=None):
	if subject==None:
		msg='''
A tool to assist with assigning and grading canvas peer reviews.  Students will get a 
grade based on a combination of the score they receive from other reviewers, and a 
score they get for how well their reviews align to other students (and the instructor).  
Their performance reviewing other studnets will be used on future assignments to determine 
their grading power.  Students whose reviews more closely align to others will have their 
reviews more heavily weighted than students whose reviews are not well aligned to others.  
Additionally, you can choose to have a students review grade adjusted to account for
how hard of a grader they are.  Both the adjustment and the grading power are adjusted 
from week to week and depend more on recent reviews than past reviews.
'''
	if subject=='parameters':
		msg='''
run getParameters() to get the grading parameters.  The first time you call it you
will be propted to enter values.  On future calls it will load those values from a
cache file unless you set the optional ignoreFile parameter to True, i.e. 
getParameters(ignoreFile=True).

You will be asked to set the number of points for each learning outcome in the rubric.
These points are relative, meaning that the final grade will be out of 100% regardless
of the total number of points in the rubric.

You will also be asked the relative weight for the creation and the review.  These two
values will be used to compute a total grade (out of 100%) for the assignment weighted 
by the entered values.

You will be asked how many reviews should be assigned to each student.  This includes 
any calibration reviews you assign.  

You are asked how many days students should have to complete the peer reviews.  When you 
an assignment due date has passed by more than this number of days it is assumed that
the reviewing is complete and ready to be graded.  Note you can enter a non-integer value
or you can simply choose not to run the program until after the review period has expired
and yo uare ready for reviews to be graded.

You are asked "How many times greater than a student should an instructors grading be 
weighted".  When assigning grades, if the instructor has evaluated a submission that 
alone will be used to determine the grade, but when calibrating other reviewers who 
also evaluated the same submissions their review grade and grading power are determined 
by a weighted average of their deviation from each other reviewer.  The average is
weighted by the grading power of the other reviewer, and the grading power of all 
students is normalized to be an average of 1.  Thus having a factor much greater than
unity will help align other students grading to yours.  A factor closer to unity will
better align students grading to each other.

You are asked for the half life of the students grading power calculations.  The idea is
that the students grading power is calculated based on how closely their reviews align
to others, but that more recent reviews should be considered more strongly in determining
this.  The weighting is exponentially decaying with the half-life being the number of
assignments before the effect of a review on the grading power is half or what it is for
the most recent assignment. 

Finally you are asked for a "compensation factor" from 0-1.  This adjusts the scores that 
reviewers give to account for their tendency to be easier or harder graders than average. 
A value of 0 does no correction, while a value of 1 attempts to completely remove this
bias.  The adjustment is done individually on each learning outcome, so a reviewer who
has a history of grading hard on a particular learning outcome but easier on another will
have their scores adjusted on both.  Note that this adjustment never allows the score on 
a learning outcome to exceed the maximum or to go below zero.
'''
	if subject=='usage':
		msg='''
To assign peer reviews including calibration reviews that you have already assessed
on canvas:

from CanvasPeerReviews import *
initialize()
params=getParameters()
getStudentWork()
assignCalibrationReviews()
assignPeerReviews(creations, numberOfReviewers=params.numberOfReviews)

To grade peer reviews that have been completed

from CanvasPeerReviews import *
students, graded_assignments, lastAssignment = initialize()
params=getParameters()
getStudentWork()
calibrate()
grade(lastAssignment)
postGrades(lastAssignment)

To view statistics on student graders:

from CanvasPeerReviews import *
initialize()
params=getParameters()
getStudentWork()
calibrate()
gradingPowerRanking()
gradingDeviationRanking()

		

'''	
	print(msg)
	msg2='''
For more help on other topics try:

cprhelp('parameters')
cprhelp('usage') 
'''
	print(msg2)