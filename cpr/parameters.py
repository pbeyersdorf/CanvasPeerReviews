#define the parameters here

class Parameters:
	def __init__(self):
		self.multiplier=dict()
		self.halfLife=9999
		self.textToPrependOnComments=""
	
	def __repr__(self):
		msg=("The parameters are:\n")
		try: # to deal with legacy data in Sp 25
			msg+=(f"    textToPrependOnComments: {self.textToPrependOnComments}\n")
		except:
			pass
		msg+=(f"    numberOfReviews: {self.numberOfReviews}\n")
		msg+=(f"    combineSubmissionAndReviewGrades: {self.combineSubmissionAndReviewGrades}\n")
		if self.combineSubmissionAndReviewGrades:
			msg+=(f"    weightingOfCreation: {self.weightingOfCreation}\n")
			msg+=(f"    weightingOfReviews: {self.weightingOfReviews}\n")
		else:
			msg+=(f"    weightingOfCreationGroup: {self.weightingOfCreationGroup}%\n")
			msg+=(f"    weightingOfReviewsGroup: {self.weightingOfReviewsGroup}%\n")		
		msg+=(f"    peerReviewDurationInDays: {self.peerReviewDurationInDays}\n")		
		msg+=(f"    compensationFactor: {self.compensationFactor}\n")
		msg+=(f"    maxCompensationFraction: {self.maxCompensationFraction}\n")
		msg+=(f"    gradingPowerForInstructors: {self.gradingPowerForInstructors}\n")
		msg+=(f"    halfLife = {self.halfLife}\n")
		msg+=(f"    reviewScoreMethod = '{self.reviewScoreMethod}'\n")
		msg+=(f"    multiplier:\n")
		
		for key in self.multiplier:
			msg+=(f"        {key}: {self.multiplier[key]}\n")
		return msg
			
	def peerReviewDurationInSeconds(self):
		#returns how long studnets are given to complete peer reviews (expressed in seconds)
		return self.peerReviewDurationInDays*24*60*60
	
	def weeklyDegradationFactor(self):
		# this returns a factor that is used to deemphasize the  calibration data for past
		# assignments.  If there is one assignment per week, then this factor is such that
		# after 'halfLife' weeks the old calibration data is only weighted by 50% relative to
		# the latest calibration data. 
		return 0.5**(1.0/self.halfLife)	
		
	def pointsForCid(self, cid, assignment, val=None):
		# if an assignment has specified the number of poinst to award for a 
		#particular criteria this will get that and return it, otherwise it will
		# return the default value stored in self.multiplier for the particular
		# criteria ID being passed as an argument.
		if assignment.pointsForCid(cid) != "default":
			return assignment.pointsForCid(cid)
		return self.multiplier[cid]
		
	def setReviewScoringMethod(self):
		print('''There are four ways that peer reviews can be scores:

	'Calibrated Grading' compares scores assigned by the reviewer
	to those given by others.  The closer the scores align the
	higher the review score.

	'compare to instructor' is similar but reviews are
	 only compared to the calibrations graded by the instructor  

	'percent completed' simply gives a score based on what percent	
	of the assigned reviews were completed.  If all reviews
	were completed a score of 100% is given

	'ignore' will not grade the peer reviews but will instead copy 
	the creation score to the review score.
	
Which method do you want to use for scoring peer reviews?''')
		try:
			currentMethod =  self.reviewScoreMethod
		except:
			currentMethod = None
		methods=["calibrated grading","compare to instructor", "percent completed", "ignore"]
		for i, method in enumerate(methods):
			if currentMethod == method:
				print(f"	{i+1}) {method} <---- current value")
			else:
				print(f"	{i+1}) {method}")
		val=0
		while val<1 or val>len(methods):
			val=input("Which method do you want to use? ")
			try:
				val=int(val)
			except:
				val=0
		self.reviewScoreMethod=methods[val-1]
		print("Set default scoring method on all assignments to be '" + self.reviewScoreMethod + "' method for review grades ")