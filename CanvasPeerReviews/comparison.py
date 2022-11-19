from datetime import datetime
import numpy as np
import pytz

class Comparison:
	# Comparison(thisGivenReview, otherReview, assignment, otherReviewer, params)
	# The comparison data records the deviation and weight 
	# for a comparison to another review
	def __init__(self,  thisGivenReview, otherReview, assignment, otherReviewer, params):	
		self.delta=dict()
		self.delta2=dict()
		self.weight=dict()
		self.date=assignment.getDate()
		self.reviewIDComparedTo=otherReview.id
		self.delta[0]=0
		self.delta2[0]=0
		self.weight[0]=0
		self.weeklyDegredationFactor=params.weeklyDegradationFactor()
		self.pointsPossible=dict()
		for cid in otherReview.scores:
			if cid in thisGivenReview.scores:
				self.delta[cid]=thisGivenReview.scores[cid] - otherReview.scores[cid]
				self.delta2[cid]=self.delta[cid]**2
				if otherReview.review_type == "peer_review":
					if otherReviewer.role == 'grader':
						weight=params.gradingPowerForGraders
					else:
						weight=otherReviewer.getGradingPower(cid); 
				elif otherReview.review_type == "grading":
					weight=params.gradingPowerForInstructors
				self.weight[cid]= weight if assignment.includeInCalibrations else 0
				self.delta[0]+=self.delta[cid]*weight
				self.delta2[0]+=self.delta2[cid]*weight
				self.weight[0]+=weight
				self.pointsPossible[cid]=assignment.criteria_points(cid)
				
		if self.weight[0]>0:
			self.delta[0]/=self.weight[0]		
			self.delta2[0]/=self.weight[0]		

	def adjustedData(self,cid, relativeValues=False):
		try:
			# return the comparison data with the weighting adjusted for its age
			now=datetime.utcnow().replace(tzinfo=pytz.UTC)
			weeksSinceDue=(now-self.date).total_seconds()/(7*24*60*60)
			degredationFactor=self.weeklyDegredationFactor**(weeksSinceDue)
			if relativeValues:
				return {'delta': self.delta[cid]/self.pointsPossible[cid], 'delta2': self.delta2[cid]/self.pointsPossible[cid], 'weight':self.weight[cid]*degredationFactor}
			else:
				return {'delta': self.delta[cid], 'delta2': self.delta2[cid], 'weight':self.weight[cid]*degredationFactor}
			
		except Exception:
			return {'delta': 0, 'delta2': 0, 'weight':0}