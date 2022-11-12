from datetime import datetime
import numpy as np

class Student:
	
	class Adjustments:
		def __init__(self, dd=None, maxGradingPower=10):
			if dd==None or dd.weight==0:
				self.compensation = 0
				self.gradingPower = 1
				self.rms=0
				self.weight = 0
			else:
				self.compensation = dd.delta/dd.weight
				self.rms= (dd.delta2/ dd.weight)**0.5
				self.weight = dd.weight
				if self.rms ==0:
					self.gradingPower=maxGradingPower
				else:
					self.gradingPower = min(maxGradingPower,(1.0/(self.rms)**2))
		
		def __repr__(self):
				return f"compensation = {round(self.compensation,2)}, gradingPower = {round(self.gradingPower,2)}" 
			
	class DeviationData:
		def __init__(self):
			self.delta=0
			self.delta2=0
			self.weight=0
		
		def addData(self, delta, weight):
			self.delta+=delta * weight
			self.delta2+=delta**2 * weight
			self.weight+=weight

		def deviation(self):
			if self.weight ==0:
				return None
			return self.delta / self.weight

		
		def rms(self):
			if self.weight ==0:
				return None
			return (self.delta2/ self.weight)**0.5
			
	def __init__(self, user):
		self.__dict__ = user.__dict__.copy() 
		self.adjustmentsByAssignment=dict()
		self.get_assignments=user.get_assignments
		self.get_missing_submissions=user.get_missing_submissions
		self.sjsuid=user.sis_user_id
		self.creations=dict()
		self.rms_deviation_by_category=dict()
		self.deviation_by_category=dict()
		self.deviation_by_category_and_assignment=dict()
		self.reviewsReceivedBy=dict()
		self.reviewsGiven=dict()
		self._assignedReviews=dict()
		self.reviewsReceived=[]
		self._gradingPower = dict()
		self.criteriaDescription=dict()
		self.submissionsCalibratedAgainst=dict()
		self.gradingPowerNormalizationFactor=dict()
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
		self.baseGradingPower=1
		self.section=0
		self.sectionName="unknown"
		self._maxGradingPower=10
		self._dataByAssignment=dict()
		self._dueDateByAssignment=dict()
					
	def getGradingPower(self,cid=0, normalize=True):
		normalizationFactor=1
		if normalize:
			try:
				normalizationFactor=self.gradingPowerNormalizationFactor[cid]
			except:
				normalizationFactor=1
		try:
			return self.adjustmentsByAssignment['current'][cid].gradingPower/normalizationFactor
		except KeyError:
			return 1

	def assignedReviewOfCreation(self, creation):
		for key in self._assignedReviews:
			for pr in self._assignedReviews[key]:
				if pr.asset_id == creation.id:
					return True
		return False
		

	def recordAssignedReview(self, assignment, peer_review):
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self._assignedReviews:
			self._assignedReviews[assignmentID]=[]
		#fingerprint="assignment_id=" + str(assignmentID) + "&author_id=" + str(peer_review.user_id) + "&reviewer_id="+str(peer_review.assessor_id)
		if not peer_review.id in [pr.id for pr in self._assignedReviews[assignmentID]]:
			self._assignedReviews[assignmentID].append(peer_review)

	def amountReviewed(self,assignment):
		assignmentID=self.idOfAssignment(assignment)
		#completed=len([1 for pr in self.assignedReviews(assignmentID) if pr.workflow_state=='completed'])
		completed=self.numberOfReviewsGivenOnAssignment(assignmentID)
		#assigned=len([1 for pr in self.assignedReviews(assignmentID)])
		assigned=self.numberOfReviewsAssignedOnAssignment(assignmentID)
		if assigned>0:
			return min(1.0,completed*1.0/assigned)
		return 0

	def recordAdjustments(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self.adjustmentsByAssignment:
			self.adjustmentsByAssignment[assignmentID]=dict()
		for cid in list(self.criteriaDescription) + [0]:
			if cid not in self.adjustmentsByAssignment[assignmentID]:
				self.adjustmentsByAssignment[assignmentID][cid]=self.Adjustments()
			self.adjustmentsByAssignment[assignmentID][cid].compensation=self.adjustmentsByAssignment['current'][cid].compensation
			self.adjustmentsByAssignment[assignmentID][cid].gradingPower=self.adjustmentsByAssignment['current'][cid].gradingPower
			self.adjustmentsByAssignment[assignmentID][cid].rms=self.adjustmentsByAssignment['current'][cid].rms
			self.adjustmentsByAssignment[assignmentID][cid].weight=self.adjustmentsByAssignment['current'][cid].weight
		
	def updateAdjustments(self, normalize=True, weeklyDegradationFactor=1, cidsToIncludeInSummarry="All"):
		compensationTotal=dict()
		delta2Total=dict()
		total=dict()
		normalizationFactor=1
		if cidsToIncludeInSummarry=="All":
			cidsToIncludeInSummarry=list(self.criteriaDescription)
		assignmentIDsInOrder=sorted(list(self._dataByAssignment),key=lambda x: -self.getDaysSinceDueDate(x))
		for cid in list(self.criteriaDescription) + [0]:
			if normalize:
				try:
					normalizationFactor=self.gradingPowerNormalizationFactor[cid]
				except:
					normalizationFactor=1
			compensationTotal[cid]=0
			delta2Total[cid]=0
			total[cid]=0
			for assignmentID in assignmentIDsInOrder:
				if not assignmentID in self.adjustmentsByAssignment:
					self.adjustmentsByAssignment[assignmentID]=dict()
				if cid not in self.adjustmentsByAssignment[assignmentID]:
					try:
						self.adjustmentsByAssignment[assignmentID][cid]=self.Adjustments(self._dataByAssignment[assignmentID][cid])
					except KeyError:
						self.adjustmentsByAssignment[assignmentID][cid]=self.Adjustments()
				if cid==0:
					compensation=0
					delta2=0
					for cid2 in cidsToIncludeInSummarry:
						compensation+=self.adjustmentsByAssignment[assignmentID][cid].compensation
						delta2+=(self.adjustmentsByAssignment[assignmentID][cid].rms)**2
					rms=(delta2/len(self.criteriaDescription))**0.5
					compensation/=len(self.criteriaDescription)
				else:					
					compensation=self.adjustmentsByAssignment[assignmentID][cid].compensation
					rms=self.adjustmentsByAssignment[assignmentID][cid].rms
					weight=self.adjustmentsByAssignment[assignmentID][cid].weight
			
				total[cid]=total[cid]*weeklyDegradationFactor+weight
				compensationTotal[cid]=compensationTotal[cid]*weeklyDegradationFactor + compensation * weight
				delta2Total[cid]=delta2Total[cid]*weeklyDegradationFactor + rms**2 * weight
				
				#record the updated values
				dd=self.DeviationData()
				dd.delta=compensationTotal[cid]
				dd.delta2=delta2Total[cid]
				dd.weight=total[cid]
				self.adjustmentsByAssignment[assignmentID][cid]=self.Adjustments(dd,self._maxGradingPower)
				
			if not 'current' in self.adjustmentsByAssignment:
				self.adjustmentsByAssignment['current']=dict()
			if not cid in self.adjustmentsByAssignment['current']:
				self.adjustmentsByAssignment['current'][cid]=self.Adjustments()
			if total[cid]>0:
				self.adjustmentsByAssignment['current'][cid].compensation = compensationTotal[cid]/total[cid]
				self.adjustmentsByAssignment['current'][cid].rms = (delta2Total[cid]/total[cid])**0.5
				if self.adjustmentsByAssignment['current'][cid].rms!=0:
					self.adjustmentsByAssignment['current'][cid].gradingPower=min(self._maxGradingPower,(1.0/(self.adjustmentsByAssignment['current'][cid].rms)**2)/normalizationFactor)
				else:
					self.adjustmentsByAssignment['current'][cid].gradingPower=self._maxGradingPower					
				self.adjustmentsByAssignment['current'][cid].weight=total[cid]
			
	def gradingReport(self, returnInsteadOfPrint=False):
		self.updateAdjustments(normalize=True)
		msg="Grading report for " + self.name +"\n"
		for cid in self.criteriaDescription:
			msg+="\t " + self.criteriaDescription[cid] +"\n"
			if cid in self.adjustmentsByAssignment['current']:
				msg+="\t\tRMS deviation of %.2f" % self.adjustmentsByAssignment['current'][cid].rms +"\n"
				msg+="\t\tAverage deviation of %+.2f" % self.adjustmentsByAssignment['current'][cid].compensation +"\n"
			msg+="\t\tGrading power for this category is %.2f" % self.adjustmentsByAssignment['current'][cid].gradingPower +"\n"
			msg+=""
		msg+="\t Overall\n"
		msg+="\t\tAverage deviation of %+.2f" % self.adjustmentsByAssignment['current'][0].compensation +"\n"
		msg+="\t\tOverall Grading power is %.2f" % self.adjustmentsByAssignment['current'][0].gradingPower +"\n"
		if returnInsteadOfPrint:
			return(msg)
		print(msg)

	def setAssignmentDueDate(self, assignment):
		self._dueDateByAssignment[assignment.id]=assignment.due_at_date

	def getDaysSinceDueDate(self, assignment):
		assignmentID=self.idOfAssignment(assignment)
		if assignmentID in self._dueDateByAssignment:
			dueDate=self._dueDateByAssignment[assignmentID]
		else:
			dueDate=datetime(2000, 1, 1, 12, 00, 00, 0)
		daysSinceDue=(int(datetime.now().strftime('%s'))-int(dueDate.strftime('%s')))/(24*60*60)
		return daysSinceDue

	def idOfAssignment(self, assignment):
		if isinstance(assignment,int):
			returnVal=assignment
		else:
			self.setAssignmentDueDate(assignment)
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
	
	def getDeviationByAssignment(self, assignment, cid=0):
		assignmentID=self.idOfAssignment(assignment)
		try:
			return self.adjustmentsByAssignment[assignmentID][cid].compensation
		except KeyError: 
			return None
			
	def getRmsByAssignment(self, assignment, cid=0):
		assignmentID=self.idOfAssignment(assignment)
		try:
			return self.adjustmentsByAssignment[assignmentID][cid].rms
		except KeyError: 
			return None

			
	def addDeviationData(self, cid, weight, thisGivenReview, otherReview):
		assignmentID=thisGivenReview.assignment_id
		if not ( (cid in thisGivenReview.scores) and (cid in otherReview.scores)):
			return
		delta=thisGivenReview.scores[cid] - otherReview.scores[cid]
		if not assignmentID in self._dataByAssignment:
			self._dataByAssignment[assignmentID]=dict()
		if cid not in self._dataByAssignment[assignmentID]:
			self._dataByAssignment[assignmentID][cid]=self.DeviationData()
		self.submissionsCalibratedAgainst[thisGivenReview.submission_id]=True
		self._dataByAssignment[assignmentID][cid].addData(delta, weight)
			
		#make an average of the data in cid=0	
		self._dataByAssignment[assignmentID][0]=self.DeviationData()
		deltaList=[self._dataByAssignment[assignmentID][cid].delta for cid in self._dataByAssignment[assignmentID] if cid!=0]
		delta2List=[self._dataByAssignment[assignmentID][cid].delta2 for cid in self._dataByAssignment[assignmentID] if cid!=0]
		weightList=[self._dataByAssignment[assignmentID][cid].weight for cid in self._dataByAssignment[assignmentID] if cid!=0]
		self._dataByAssignment[assignmentID][0].delta=np.average(deltaList)
		self._dataByAssignment[assignmentID][0].delta2=np.average(delta2List)
		self._dataByAssignment[assignmentID][0].weight=np.average(weightList)
		