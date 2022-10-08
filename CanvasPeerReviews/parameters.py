#define the parameters here

class Parameters:
	def __init__(self):
		self.multiplier=dict()
		self.halfLife=9999
	
	def peerReviewDurationInSeconds(self):
		return self.peerReviewDurationInDays*24*60*60
	
	def weeklyDegradationFactor(self):
		return 0.5**(1.0/self.halfLife)	
		
	def setPoints(self, assignment):
		for criteria in assignment.rubric:
			cid=criteria['id']
			val=input("How many points (out of 100) for '" + criteria['description'] + "' creiteria [" +str( self.multiplier[cid])+ "]? ")
			try:
				val=float(val)
			except:
				val=self.multiplier[cid]
			key="assignment=" + str(assignment.id) + "&criteria=" + str(cid)
			print("setting multiplier[" + key + "]=" + str(val))
			self.multiplier[key]=val

	def pointsForCid(self, cid, assignmentid, val=None):
		key="assignment=" + str(assignmentid) + "&criteria=" + str(cid)
		if val!=None:
			self.multiplier[key]=val
			return
		if key in self.multiplier:
			return self.multiplier[key]
		else:
			return self.multiplier[cid]