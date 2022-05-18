class Student:

	def __init__(self, user):
		self.__dict__ = user.__dict__.copy() 
		self.get_assignments=user.get_assignments
		self.get_missing_submissions=user.get_missing_submissions
		self.sjsuid=user.sis_user_id
		self.creations=dict()
		self.rms_deviation_by_category=dict()
		self.deviation_by_category=dict()
		self.number_of_reviews=0
		self.reviewsGiven=dict()
		self.reviewsReceived=[]
		self.gradingPower = dict()
		self.delta2=dict()
		self.delta=dict()
		self.LODescription=dict()
		self.numberOfComparisons=dict()
		self.submissionsCalibratedAgainst=dict()
		self.gradingPowerNormalizatoinFactor=dict()
		self.grades=dict()
		self.comments=dict()
		self.reviewCount=dict()
		self.assignmentsGradedByInstructor=dict()
		self.gradesByLO=dict()
		self.assignmentsCalibrated=dict()
		self.role="student"
		

	def getGradingPower(self,LOid):
		if not LOid in self.gradingPowerNormalizatoinFactor:
			self.gradingPowerNormalizatoinFactor[LOid] = 1
		if not LOid in self.gradingPower:
			self.gradingPower[LOid] = 1
			return 1
		if (self.gradingPower[LOid]==1):
			return 1
		return min(10,self.gradingPower[LOid]/self.gradingPowerNormalizatoinFactor[LOid])

	def getDeviation(self,LOid):
		if not LOid in self.deviation_by_category:
			return 0
		return self.deviation_by_category[LOid]



	def getGradingPowerNormalizatoinFactor(self, LOid):
		try:
			return self.gradingPowerNormalizatoinFactor[LOid]
		except:
			return 1

	def updateGradingPower(self):
		total=0
		totalDeviation=0
		cnt=0
		for LOid in self.delta2:
			if not LOid in self.deviation_by_category:
				self.deviation_by_category[LOid]=0
			try:
				if (self.numberOfComparisons[LOid]>2):
					self.rms_deviation_by_category[LOid] = (self.delta2[LOid] / max(0.1,self.numberOfComparisons[LOid]-1))**0.5
					if self.numberOfComparisons[LOid]==0:
						self.deviation_by_category[LOid] =0
					else:	
						self.deviation_by_category[LOid] = (self.delta[LOid] / self.numberOfComparisons[LOid])
					self.gradingPower[LOid]=(1.0/self.rms_deviation_by_category[LOid]**2)/self.getGradingPowerNormalizatoinFactor(LOid)
					total+=self.gradingPower[LOid]
					totalDeviation+=self.deviation_by_category[LOid]
					cnt+=1
				else:
					self.gradingPower[LOid]=1
					total+=self.gradingPower[LOid]
					totalDeviation+=self.deviation_by_category[LOid]
					cnt+=1
			except:
				self.gradingPower[LOid]=1
				total+=self.gradingPower[LOid]
				totalDeviation+=self.deviation_by_category[LOid]
				cnt+=1
		if cnt!=0:
			self.gradingPower[0]=total/cnt	
			self.deviation_by_category[0]=totalDeviation/cnt
		else:
			self.gradingPower[0]=1
			self.deviation_by_category[0]=0
			
	def gradingReport(self, returnInsteadOfPrint=False):
		self.updateGradingPower()
		msg="Grading report for " + self.name +"\n"
		for LOid in self.delta2:
			msg+="\t " + self.LODescription[LOid] +"\n"
#			msg+="\t '" + str(LOid) +"'\n"
			if LOid in self.rms_deviation_by_category and LOid in self.deviation_by_category:
				msg+="\t\tRMS deviation of %.2f" % self.rms_deviation_by_category[LOid] +"\n"
				msg+="\t\tAverage deviation of %+.2f" % self.deviation_by_category[LOid] +"\n"
			msg+="\t\tGrading power for this category is %.2f" % self.gradingPower[LOid] +"\n"
			msg+=""
		if returnInsteadOfPrint:
			return(msg)
		print(msg)
		
	def numberOfReviewsGivenOnAssignment(self, assignment_id):
		relevantReviews=dict()
		for key,review in self.reviewsGiven.items():
			if review.assignment_id == assignment_id:
				relevantReviews[review.submission_id]=True
		return len(relevantReviews)
			
			
