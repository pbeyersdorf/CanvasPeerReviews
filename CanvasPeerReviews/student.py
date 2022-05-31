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
		self.criteriaDescription=dict()
		self.numberOfComparisons=dict()
		self.submissionsCalibratedAgainst=dict()
		self.gradingPowerNormalizatoinFactor=dict()
		self.points=dict()
		self.grades=dict()
		self.comments=dict()
		self.reviewCount=dict()
		self.assignmentsGradedByInstructor=dict()
		self.pointsByCriteria=dict()
		self.assignmentsCalibrated=dict()
		self.role="student"
		

	def getGradingPower(self,cid):
		if not cid in self.gradingPowerNormalizatoinFactor:
			self.gradingPowerNormalizatoinFactor[cid] = 1
		if not cid in self.gradingPower:
			self.gradingPower[cid] = 1
			return 1
		if (self.gradingPower[cid]==1):
			return 1
		return min(10,self.gradingPower[cid]/self.gradingPowerNormalizatoinFactor[cid])

	def getDeviation(self,cid):
		if not cid in self.deviation_by_category:
			return 0
		return self.deviation_by_category[cid]



	def getGradingPowerNormalizatoinFactor(self, cid):
		try:
			return self.gradingPowerNormalizatoinFactor[cid]
		except:
			return 1

	def updateGradingPower(self):
		total=0
		totalDeviation=0
		cnt=0
		for cid in self.delta2:
			if not cid in self.deviation_by_category:
				self.deviation_by_category[cid]=0
			try:
				if (self.numberOfComparisons[cid]>2):
					self.rms_deviation_by_category[cid] = (self.delta2[cid] / max(0.1,self.numberOfComparisons[cid]-1))**0.5
					if self.numberOfComparisons[cid]==0:
						self.deviation_by_category[cid] =0
					else:	
						self.deviation_by_category[cid] = (self.delta[cid] / self.numberOfComparisons[cid])
					self.gradingPower[cid]=(1.0/self.rms_deviation_by_category[cid]**2)/self.getGradingPowerNormalizatoinFactor(cid)
					total+=self.gradingPower[cid]
					totalDeviation+=self.deviation_by_category[cid]
					cnt+=1
				else:
					self.gradingPower[cid]=1
					total+=self.gradingPower[cid]
					totalDeviation+=self.deviation_by_category[cid]
					cnt+=1
			except:
				self.gradingPower[cid]=1
				total+=self.gradingPower[cid]
				totalDeviation+=self.deviation_by_category[cid]
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
		for cid in self.delta2:
			msg+="\t " + self.criteriaDescription[cid] +"\n"
#			msg+="\t '" + str(cid) +"'\n"
			if cid in self.rms_deviation_by_category and cid in self.deviation_by_category:
				msg+="\t\tRMS deviation of %.2f" % self.rms_deviation_by_category[cid] +"\n"
				msg+="\t\tAverage deviation of %+.2f" % self.deviation_by_category[cid] +"\n"
			msg+="\t\tGrading power for this category is %.2f" % self.gradingPower[cid] +"\n"
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
			
			
