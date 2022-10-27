class Student:

	def __init__(self, user):
		self.__dict__ = user.__dict__.copy() 
		self.get_assignments=user.get_assignments
		self.get_missing_submissions=user.get_missing_submissions
		self.sjsuid=user.sis_user_id
		self.creations=dict()
		self.rms_deviation_by_category=dict()
		self.rms_deviation_by_assignment=dict()
		self.deviation_by_category=dict()
		self.reviewsReceivedBy=dict()
		self.reviewsGiven=dict()
		self._assignedReviews=dict()
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
		self.regrade=dict()
		self.comments=dict()
		self.reviewData=dict()
		self.givenReviewData=dict()
		self.regradeComments=dict()
		self.reviewCount=dict()
		self.assignmentsGradedByInstructor=dict()
		self.pointsByCriteria=dict()
		#self.assignmentsCalibrated=dict()
		self.role="student"
		self.section=0
		self.sectionName="unknown"
		self._maxGradingPower=10

					
	def getGradingPower(self,cid):
		if not cid in self.gradingPowerNormalizatoinFactor:
			self.gradingPowerNormalizatoinFactor[cid] = 1
		if not cid in self.gradingPower:
			self.gradingPower[cid] = 1
			return 1
		if (self.gradingPower[cid]==1):
			return 1
		return min(self._maxGradingPower,self.gradingPower[cid]/self.gradingPowerNormalizatoinFactor[cid])

	def getDeviation(self,cid):
		if not cid in self.deviation_by_category:
			return 0
		return self.deviation_by_category[cid]

	def getGradingPowerNormalizatoinFactor(self, cid):
		return 1
		try:
			return self.gradingPowerNormalizatoinFactor[cid]
		except:
			return 1

	def recordAssignedReview(self, assignment, peer_review):
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self._assignedReviews:
			self._assignedReviews[assignmentID]=[]
		#fingerprint="assignment_id=" + str(assignmentID) + "&author_id=" + str(peer_review.user_id) + "&reviewer_id="+str(peer_review.assessor_id)
		if not peer_review.id in [pr.id for pr in self._assignedReviews[assignmentID]]:
			self._assignedReviews[assignmentID].append(peer_review)
			#print("adding review #" + str(peer_review.id) + " to " + self.name +"'s list of assigned reviews" )
			

	def amountReviewed(self,assignment):
		assignmentID=self.idOfAssignment(assignment)
		#completed=len([1 for pr in self.assignedReviews(assignmentID) if pr.workflow_state=='completed'])
		completed=self.numberOfReviewsGivenOnAssignment(assignmentID)
		#assigned=len([1 for pr in self.assignedReviews(assignmentID)])
		assigned=self.numberOfReviewsAssignedOnAssignment(assignmentID)
		if assigned>0:
			return min(1.0,completed*1.0/assigned)
		return 0

	def updateGradingPower(self, normalize=True):
		total=0
		totalDeviation=0
		cnt=0
		for cid in self.delta2:
			if normalize:
				normalizationFactor=self.getGradingPowerNormalizatoinFactor(cid)
			else:
				normalizationFactor=1
		
			if not cid in self.deviation_by_category:
				self.deviation_by_category[cid]=0
			try:
				if (self.numberOfComparisons[cid]>2):
					self.rms_deviation_by_category[cid] = (self.delta2[cid] / max(0.1,self.numberOfComparisons[cid]-1))**0.5
					if self.numberOfComparisons[cid]==0:
						self.deviation_by_category[cid] =0
					else:	
						self.deviation_by_category[cid] = (self.delta[cid] / self.numberOfComparisons[cid])
					self.gradingPower[cid]=min(self._maxGradingPower,(1.0/self.rms_deviation_by_category[cid]**2)/normalizationFactor)
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
		if normalize:
			normalizationFactor=self.getGradingPowerNormalizatoinFactor(0)
		else:
			normalizationFactor=1
		if cnt!=0:
			self.gradingPower[0]=min(self._maxGradingPower,(total/cnt)/normalizationFactor)
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
		msg+="\t Overall\n"
		msg+="\t\tAverage deviation of %+.2f" % self.deviation_by_category[0] +"\n"
		msg+="\t\tOverall Grading power is %.2f" % self.gradingPower[0] +"\n"
		if returnInsteadOfPrint:
			return(msg)
		print(msg)

	def idOfAssignment(self, assignment):
		if isinstance(assignment,int):
			returnVal=assignment
		else:
			returnVal=assignment.id
		return returnVal

	def assignedReviews(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		if assignmentID not in self._assignedReviews:
			self._assignedReviews[assignmentID]=[]
		return self._assignedReviews[assignmentID]

	def numberOfReviewsAssignedOnAssignment(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		return len(self.assignedReviews(assignmentID))

	def removeAssignedReview(self, peer_review):
		for key in self._assignedReviews:
			for i,assignedReview in enumerate(self._assignedReviews[key]):
				if assignedReview.id==peer_review.id:
					del self._assignedReviews[key][i]
	

	def numberOfReviewsGivenOnAssignment(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		relevantReviews=dict()
		for key,review in self.reviewsGiven.items():
			if review.assignment_id == assignmentID:
				relevantReviews[review.submission_id]=True
		return len(relevantReviews)

	def numberOfReviewsReceivedOnAssignment(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		count=0
		for review in self.reviewsReceived:
			if review.assignment_id == assignmentID:
				count+=1
		return count
	
	def graderIDsForAssignment(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		try:
			flat_list = [item['reviewerID'] for sublist in (list(self.reviewData[assignmentID].values())) for item in sublist]
			return flat_list
		except:
			return []
	
	def pointsOnAssignment(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self.reviewData:
			try:
				print("No reviews of work on " + assignment.name)
			except:
				print("No reviews of work on assignment with id=" + str(assignmentID))
			return
		for key in self.reviewData[assignmentID]:
			points=0
			adjpoints=0
			weights=0
			pointsString="("
			weightsString="["
			compString="{"
			for a in self.reviewData[assignmentID][key]:
				points+=a['points']
				adjpoints+=a['weight']*(a['points']-a['compensation'])
				weights+=a['weight']
				pointsString+='{:.4s}'.format('{:0.4f}'.format(a['points'])) + ", "
				weightsString+='{:.4s}'.format('{:0.4f}'.format(a['weight']))	 + ", "
				compString+='{:.4s}'.format('{:0.4f}'.format(a['compensation']))	 + ", "
				#weightsString+=str(a['weight']) + ", "
			pointsString=pointsString[:-2]+ ") points"
			weightsString=weightsString[:-2]+ "] weights"
			compString=compString[:-2]+ "} compensations"
			#print(self.reviewData[assignmentID][key][0]['description'], round(adjpoints/weights,2), pointsString)
			if weights!=0:
				avgStr=str(round(adjpoints/weights,2))
			else:
				avgStr='err'
			print('{0: <30}'.format(self.reviewData[assignmentID][key][0]['description'])+'{0: <7}'.format(avgStr)+pointsString)
			print('{0: <30}'.format("")+'{0: <7}'.format("")+ weightsString)
			print('{0: <30}'.format("")+'{0: <7}'.format("")+ compString)
