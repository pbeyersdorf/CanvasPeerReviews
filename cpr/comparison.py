from datetime import datetime
import numpy as np
import pytz

class Comparison:
	# Comparison(thisGivenReview, otherReview, assignment, otherReviewer, params)
	# The comparison data records the deviation and weight 
	# for a comparison to another review
	def __init__(self,  thisGivenReview, otherReview, assignment, studentsById, params):	
		self.delta=dict()
		self.delta2=dict()
		self.weight=dict()
		self.originalUpdatedWeight=dict()
		self.date=assignment.getDate()
		self.reviewIDComparedTo=otherReview.id
		self.reviewID=thisGivenReview.id
		self.delta[0]=0
		self.delta2[0]=0
		self.weight[0]=0
		self.weeklyDegredationFactor=params.weeklyDegradationFactor()
		self.pointsPossible=dict()
		self.updateable=False
		self.otherReviewType=otherReview.review_type
		self.assignment_id=assignment.id
		self.creation_id=thisGivenReview.creation.id
		self.thisReviewId=thisGivenReview.id
		self.thisReviewType=thisGivenReview.review_type
		self.thisReviewReviewerId=thisGivenReview.reviewer_id
		self.otherReviewId=otherReview.id
		self.otherReviewType=otherReview.review_type
		self.otherReviewReviewerId=otherReview.reviewer_id
		self.authorName=studentsById[thisGivenReview.author_id].name
		if thisGivenReview.reviewer_id in studentsById:
			self.thisReviewerName=studentsById[thisGivenReview.reviewer_id].name
		else:
			self.thisReviewerName=thisGivenReview.reviewer_id
		if otherReview.reviewer_id in studentsById:
			self.otherReviewerName=studentsById[otherReview.reviewer_id].name
		else:
			self.otherReviewerName=otherReview.reviewer_id
		self.assignmentName=assignment.name

		for cid in otherReview.scores:
			if cid in thisGivenReview.scores:
				self.delta[cid]=thisGivenReview.scores[cid] - otherReview.scores[cid]
				self.delta2[cid]=self.delta[cid]**2
				if otherReview.review_type == "peer_review":
					if otherReview.reviewer_id in studentsById:
						otherReviewer=studentsById[otherReview.reviewer_id]
						if otherReviewer.role == 'grader':
							weight=params.gradingPowerForGraders
						else:
							weight=otherReviewer.getGradingPower(cid)
							self.updateable=assignment.includeInCalibrations
					else:
						weight=0 # the student dropped the class, so let's not count this review
				elif otherReview.review_type == "grading":
					weight=params.gradingPowerForInstructors
				self.weight[cid]= weight if assignment.includeInCalibrations else 0
				self.delta[0]+=self.delta[cid]*weight
				self.delta2[0]+=self.delta2[cid]*weight
				self.weight[0]+=weight if assignment.includeInCalibrations else 0
				self.pointsPossible[cid]=assignment.criteria_points(cid)
				
		if self.weight[0]>0:
			self.delta[0]/=self.weight[0]		
			self.delta2[0]/=self.weight[0]		

	def __repr__(self):
		msg=""
		try:
			msg+=(f"Comparison of review ({self.thisReviewId}) to ({self.otherReviewId}) on assignment ({self.assignment_id})\n")
			try:
				msg+=(f"This review of {self.authorName}'s submission \n\tis by {self.thisReviewerName} ({self.thisReviewType}) \n\tand is compared to review by {self.otherReviewerName} ({self.otherReviewType}) \n\tfor asignment {self.assignmentName}")
			except:
				msg+="error"
				msg+=(f"This review of {self.authorName}'s submission \n\tis by user id {self.thisReviewReviewerId} ({self.thisReviewType}) \n\tand is compared to review by uer id {self.otherReviewReviewerId} ({self.otherReviewType}) \n\tfor asignment {self.assignmentName}")
		except:
			msg+="Comprison Object (possibly incomplete)"
		return msg

	def updateWeight(self, otherReviewer):
		if not self.updateable:
			return
		for cid in self.weight:
			self.weight[cid]= otherReviewer.getGradingPower(cid)
			if not cid in self.originalUpdatedWeight:
				self.originalUpdatedWeight[cid]=self.weight[cid]

	def adjustedData(self,cid, relativeValues=False, degraded=True, useOriginalUpdatedWeight=True):
		try:
			if useOriginalUpdatedWeight and cid not in self.originalUpdatedWeight:
				raise Exception("requested original weight of comparion that has not been updated yet")
			# return the comparison data with the weighting adjusted for its age
			now=datetime.utcnow().replace(tzinfo=pytz.UTC)
			weeksSinceDue=(now-self.date).total_seconds()/(7*24*60*60)
			degredationFactor = 1 if not degraded else self.weeklyDegredationFactor**(weeksSinceDue)
			weight=self.originalUpdatedWeight[cid] if useOriginalUpdatedWeight else self.weight[cid]
			if relativeValues:
				return {'delta': self.delta[cid]/self.pointsPossible[cid], 'delta2': self.delta2[cid]/self.pointsPossible[cid], 'weight':weight*degredationFactor}
			else:
				return {'delta': self.delta[cid], 'delta2': self.delta2[cid], 'weight':weight*degredationFactor}
			
		except Exception:
			return {'delta': self.delta[cid], 'delta2': self.delta2[cid], 'weight':self.weight[cid]}
			#return {'delta': 0, 'delta2': 0, 'weight':0}