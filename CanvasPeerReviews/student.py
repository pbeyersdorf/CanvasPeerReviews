from datetime import datetime
import numpy as np
import copy
import pytz

class Student:
	
	class Adjustments:
		# this class defines how much the scores the student awards on a peer
		# review should be adjusted (the compensation value gets added to the score 
		# they gave) and how strongly they should count relative to tother 
		# students (gradingPower)
		#def __init__(self, dd=None, maxGradingPower=10):
		def __init__(self, delta, delta2, weight, maxGradingPower=10):
			if weight!=0:
				self.deviation=delta/weight
				self.rms=(delta2/weight)**0.5
			else:
				self.deviation=0
				self.rms=0
			self.compensation=-self.deviation
			self.weight=weight
			self.maxGradingPower=maxGradingPower
			self.gradingPowerNormalizationFactor=1

					
		def gradingPower(self, normalizationFactor=1):
			if self.rms==0 and self.weight!=0:
				return self.maxGradingPower
			elif self.weight!=0 and normalizationFactor=="auto":
				return min(self.maxGradingPower,(1.0/(self.rms)**2)/self.gradingPowerNormalizationFactor)
			elif self.weight!=0:
				return min(self.maxGradingPower,(1.0/(self.rms)**2)/normalizationFactor)
			return 1
							
		#def __repr__(self):
		#		return f"comp : {round(self.compensation,2)}, gradPow: {round(self.gradingPower,2)}, rms: {round(self.rms,2)}, weight: {round(self.weight,2)}" 

					
	def __init__(self, user):
		self.__dict__ = user.__dict__.copy() 
		self.adjustmentsByAssignment=dict()
		self.adjustments=dict()
		self.get_assignments=user.get_assignments
		self.get_missing_submissions=user.get_missing_submissions
		self.sjsuid=user.sis_user_id
		self.creations=dict()
		self.submissionPlaceholders=dict()
		self.reviewsGiven=dict()
		self._assignedReviews=dict()
		self.reviewsReceived=[]
		self.criteriaDescription=dict()
		self.gradingPowerNormalizationFactor=dict()
		self.points=dict()
		self.grades=dict()
		self.regrade=dict()
		self.comments=dict()
		self.reviewData=dict()
		self.givenReviewData=dict()
		self.regradeComments=dict()
		self.assignmentsGradedByInstructor=dict()
		self.pointsByCriteria=dict()
		self.role="student"
		#self.baseGradingPower=1
		self.section=0
		self.sectionName="unknown"
		self.maxGradingPower=5
		#._dueDateByAssignment=dict()
		self.rmsByAssignment=dict()
		self.comparisons=dict()

					
	def getGradingPower(self,cid=0, normalize=True):
		# returns the grading power for this students for the given criteria ID
		# when normalized it uses the gradingPowerNormalizationFactor which is 
		# meant ot be set as the average grading power for all studnets, but must
		# be calculated and set from outside this class, since calculating it 
		# requires access to ALL student data.
		if cid not in self.gradingPowerNormalizationFactor:
			print("no normalizatoin factor set")
			self.gradingPowerNormalizationFactor[cid]=1
		normalizationFactor=self.gradingPowerNormalizationFactor[cid]
			
		try:
			return self.adjustments[cid].gradingPower(normalizationFactor)
		except:
			return 1

	def assignedReviewOfCreation(self, creation):
		# when passed a creation object will return True/False based on if that
		# creation has been assigned to this user.
		for key in self._assignedReviews:
			for pr in self._assignedReviews[key]:
				if pr.asset_id == creation.id:
					return True
		return False
		

	def recordAssignedReview(self, assignment, peer_review):
		# this adds a given peer_review object to the internal list _assignedReviews
		# of reviews that have been assigned to this student, organized in a dictionary
		# based on the assignment id.  It will create a dictionary entry if necessary 
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self._assignedReviews:
			self._assignedReviews[assignmentID]=[]
		if not peer_review.id in [pr.id for pr in self._assignedReviews[assignmentID]]:
			self._assignedReviews[assignmentID].append(peer_review)

	def amountReviewed(self,assignment):
		# returns a number from 0-1 representing the fraction of the total number of 
		# peer reviews assigned on a given assignment have been completed.  Useful
		# for keeping track of review progress and for assigning grades based on 
		# how complete the students peer reviews are on an assignment.   
		assignmentID=self.idOfAssignment(assignment)
		completed=self.numberOfReviewsGivenOnAssignment(assignmentID)
		assigned=self.numberOfReviewsAssignedOnAssignment(assignmentID)
		if assigned>0:
			return min(1.0,completed*1.0/assigned)
		return 0

	def recordAdjustments(self, assignment):
		# when grading an assignment, take the adjustments being used defined by 
		# self.adjustments and add it to a dictionary keyed to 
		# the assignment ID for later reference.  
		assignmentID=self.idOfAssignment(assignment)
		if not assignmentID in self.adjustmentsByAssignment:
			self.adjustmentsByAssignment[assignmentID]=dict()
		for cid in list(self.criteriaDescription) + [0]:
			self.adjustmentsByAssignment[assignmentID][cid]=copy.deepcopy(self.adjustments[cid]) 
			self.adjustmentsByAssignment[assignmentID][cid].gradingPowerNormalizationFactor = self.gradingPowerNormalizationFactor[cid]



	def updateAdjustments(self, normalize=True, weeklyDegradationFactor=1, cidsToIncludeInSummary="All",  endDate=datetime.utcnow().replace(tzinfo=pytz.UTC)):
		# go through all of the comparisons on all prior assignments in order accumulating the data
		# while degrading older data to get the current compensation parameters
		if cidsToIncludeInSummary=="All":
			cidsToIncludeInSummary=list(self.criteriaDescription)
		cidsToIncludeInSummary+=[0]
		self.adjustments=dict()
		#if not 'current' in self.adjustmentsByAssignment:
		#	self.adjustments=dict()
		for cid in cidsToIncludeInSummary:	
			if not normalize:
				self.gradingPowerNormalizationFactor[cid]=1
			totalDelta=0
			totalDelta2=0
			totalWeight=0
			for key in self.comparisons:
				adjustedData=self.comparisons[key].adjustedData(cid)
				beforeEndDate=(endDate-self.comparisons[key].date).total_seconds()>0
				if beforeEndDate:
					totalDelta+=adjustedData['delta']*adjustedData['weight']
					totalDelta2+=adjustedData['delta2']*adjustedData['weight']
					totalWeight+=adjustedData['weight']
			self.adjustments[cid]=self.Adjustments(totalDelta, totalDelta2, totalWeight, self.maxGradingPower)
			if cid in self.gradingPowerNormalizationFactor:
				self.adjustments[cid].gradingPowerNormalizationFactor=self.gradingPowerNormalizationFactor[cid]
			else:
				self.adjustments[cid].gradingPowerNormalizationFactor=1
			
			

	def gradingReport(self, returnInsteadOfPrint=False):
		self.updateAdjustments(normalize=True)
		msg="Grading report for " + self.name +"\n"
		for cid in self.criteriaDescription:
			msg+="\t " + self.criteriaDescription[cid] +"\n"
			if cid in self.adjustments:
				msg+="\t\tRMS deviation of %.2f" % self.adjustments[cid].rms +"\n"
				msg+="\t\tAverage compensation of %+.2f" % self.adjustments[cid].compensation +"\n"
			msg+="\t\tGrading power for this category is %.2f" % self.adjustments[cid].gradingPower() +"\n"
			msg+=""
		msg+="\t Overall\n"
		msg+="\t\tAverage deviation of %+.2f" % self.adjustments[0].compensation +"\n"
		msg+="\t\tOverall Grading power is %.2f" % self.adjustments[0].gradingPower() +"\n"
		if returnInsteadOfPrint:
			return(msg)
		print(msg)

		


# 	def setAssignmentDueDate(self, assignment):
# 		self._dueDateByAssignment[assignment.id]=assignment.due_at_date

# 	def getDaysSinceDueDate(self, assignment):
# 		assignmentID=self.idOfAssignment(assignment)
# 		if assignmentID in self._dueDateByAssignment:
# 			dueDate=self._dueDateByAssignment[assignmentID]
# 		else:
# 			dueDate=datetime(2000, 1, 1, 12, 00, 00, 0)
# 		daysSinceDue=(int(datetime.now().strftime('%s'))-int(dueDate.strftime('%s')))/(24*60*60)
# 		return daysSinceDue

	def idOfAssignment(self, assignment):
		if isinstance(assignment,int):
			returnVal=assignment
		else:
			#self.setAssignmentDueDate(assignment)
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
		