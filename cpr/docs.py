from cpr.utilities import *

print("cprhelp() for information")

def cprhelp(subject=None):
	if subject==None:
		msg="A tool to assist with assigning and grading canvas peer reviews.  Students will get a  grade based on a combination of their creation (score they receive from other reviewers),  and a their reviews (how well their reviews align to other students and the instructor).   Their performance reviewing other students will be used on future assignments to determine  their grading power.  Students whose reviews more closely align to others will have their  reviews more heavily weighted than students whose reviews are not well aligned to others.   Additionally, you can choose to have a students review grade adjusted to account for how hard of a grader they are.  Both the adjustment and the grading power are evaluated independently for each rubric criteria and adjusted are updated from week to week and  can depend more on recent reviews than past reviews."
	if subject=='parameters':
		msg='''
		run getParameters() to get the grading parameters.  The first time you call it you will be propted to enter values.  On future calls it will load those values from a cache file unless you set the optional ignoreFile parameter to True, i.e.  getParameters(ignoreFile=True).

You will be asked to set the number of points for each learning outcome in the rubric. These points are relative, meaning that the final grade will be out of 100% regardless of the total number of points in the rubric.

You will also be asked the relative weight for the creation and the review.  These two values will be used to compute a total grade (out of 100%) for the assignment weighted  by the entered values.

You will be asked how many reviews should be assigned to each student submission.   Each student will be assigned at least this many reviews, possibly one more.

You are asked how many days students should have to complete the peer reviews. This can be used in scripts to verify when an assignment should be graded.

You are asked 'How many times greater than a student should an instructors grading be  weighted'.  When assigning grades, if the instructor has evaluated a submission that  alone will be used to determine the grade, but when calibrating other reviewers who  also evaluated the same submissions their review grade and grading power are determined  by a weighted average of their deviation from each other reviewer.  The average is weighted by the grading power of the other reviewer, and the grading power of all  students is normalized to be an average of 1.  Thus having a factor much greater than unity will help align other students grading to yours.  A factor closer to unity will better align students grading to each other.

You are asked for the half life of the students grading power calculations.  The idea is that the students grading power is calculated based on how closely their reviews align to others, but that more recent reviews should be considered more strongly in determining this.  The weighting is exponentially decaying with the half-life being the number of assignments before the effect of a review on the grading power is half or what it is for the most recent assignment. 

Finally you are asked for a 'compensation factor' from 0-1.  This adjusts the scores that  reviewers give to account for their tendency to be easier or harder graders than average.  A value of 0 does no correction, while a value of 1 attempts to completely remove this bias.  The adjustment is done individually on each learning outcome, so a reviewer who has a history of grading hard on a particular learning outcome but easier on another will have their scores adjusted differently on each.  Note that this adjustment never allows  the score on a learning outcome to exceed the maximum or to go below zero, however it can result ina student who received the maximum (or minimum) grade from each reviewer to get assigned a score that is less than the maximum (or greater than the minimum). 
		'''
	if subject=='usage':
		msg='''
To assign peer reviews including calibration reviews that you have already assessed on canvas:

from cpr import *
initialize()
params=getParameters()
getStudentWork()
assignCalibrationReviews()
assignPeerReviews(creations, numberOfReviewers=params.numberOfReviews)

To grade peer reviews that have been completed

from cpr import *
students, graded_assignments, lastAssignment = initialize()
params=getParameters()
getStudentWork()
calibrate()
grade(lastAssignment)
postGrades(lastAssignment)

To view statistics on student graders:

from cpr import *
initialize()
params=getParameters()
getStudentWork()
calibrate()
gradingPowerRanking()
gradingDeviationRanking()
		

'''	
	if subject=='grading':
		msg='''
Raw grades are computed based on the percentage earned for each rubric criteria times a weighting for that rubric criteria that has its default value defined by the user the first time getParameters() is called.  It can be overridden for a particular assignment object, by calling the setPoints() parameter of the object.  So for instance to choose an assignment and set its point distribution use

activeAssignment=chooseAssignment()activeAssignment.setPoints()

There are three methods for dealing with peer reviews - ignore, percent complete, and calibrated grading.  The method is stored as a property of the assignment object and can be set by calling assignment.setReviewScoringMethod().  The default is 'calibrated grading'.  When the method is 'ignore' the creation grade is used to determine the final grade with no dependence on the review scoring.  When the method is 'percent complete' the review score is base only on having completed the peer reviews, not on their quality.  

For the 'calibrated grading' method the score for the reviews is based on a weighted RMS deviation of the students given review scores from all other reviewers of the same creations.  The reviewCurve() property of each assignment object defines the equation that converts this rms value into a score.  The default is 'max(0,min(100, 120*(1-1.1*rms)))' as defined in assignment.py.  To choose an assignment and overwrite this curve use

activeAssignment=chooseAssignment()
activeAssignment.reviewCurve=new_review_curve

where new_review_curve is a string of text that when evaluated in python will calculatea score based on the value of the variable 'rms'.

Within the grade(assignment) function the creation and review scores are calculated and combined using the weighting defined the first time that getParameters() is called.This combined score can then be curved based on a text string the user will be prompted for which when evaluated as a python expression would calculate a score based on the variable 'x' that represents the students raw score.  For example 'x+10' would add 10 points to the raw score.  'round(min(x+10,100)) would add 10 points, limiting the high score to 100 and round the calculated value to the nearest integer.

Whatever functions and weightings used to calculate a score gets recorded to a log fileso that it can be reused for any future regrading on the assignment.

Students can request a regrade by entering a comment on their assignment with a keyword in it.  The default keywords are defined in the regrade() function in utilities.py and are 'regrade' to request the creation be regraded, and 'recalculate' to request the peer review score be recalculated based on comparisons only to a calibration review performed by the instructor.'''
	msg2='''
For more help on other topics try:

cprhelp('parameters')
cprhelp('usage') 
cprhelp('grading') 
'''

	printWithWrapping(msg)
	print(Style.BRIGHT + msg2 + Style.RESET_ALL)