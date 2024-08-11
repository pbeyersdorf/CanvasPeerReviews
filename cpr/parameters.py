#define the parameters here

class Parameters:
	def __init__(self):
		self.multiplier=dict()
		self.halfLife=9999
	
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