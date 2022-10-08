#define the parameters here

class Parameters:
	def __init__(self):
		self.multiplier=dict()
		self.halfLife=9999
	
	def peerReviewDurationInSeconds(self):
		return self.peerReviewDurationInDays*24*60*60
	
	def weeklyDegradationFactor(self):
		return 0.5**(1.0/self.halfLife)	
		
	def pointsForCid(self, cid, assignment, val=None):
		if assignment.pointsForCid(cid) != "default":
			return assignment.pointsForCid(cid)
		return self.multiplier[cid]