from datetime import datetime, timedelta
import pytz

class GradedAssignment:
	def __init__(self, assignment):	
		if hasattr(assignment, 'rubric'):
			for outcome in assignment.rubric:
				if not 'id' in outcome:
					outcome['id']=None
		self.__dict__ = assignment.__dict__.copy() 
		self.graded = False 
		self.gradesPosted = False 
		self.regraded = False 
		self.peer_reviews_assigned = False
		self.get_peer_reviews=assignment.get_peer_reviews
		self.get_submissions=assignment.get_submissions
		self.multiplier=dict()
		self.curve='x'
		self.reviewCurve='max(0,min(100, 120*(1-1.1*rms)))'
		self.regradesCompleted=False
		self.date=self.getDate(assignment)
		self.pointsByCidOverride=dict()
		self.reviewScoreMethod="calibrated grading"

	def sync(self, assignment):
		if assignment.id == self.id:
			self.__dict__.update(assignment.__dict__)
			self.date=self.getDate(assignment)
	
	def setReviewScoringMethod(self):
		print()
		try:
			currentMethod =  self.reviewScoreMethod
		except:
			self.reviewScoreMethod = "calibrated grading"
			currentMethod =  self.reviewScoreMethod
		methods=["calibrated grading","percent completed", "ignore"]
		for i, method in enumerate(methods):
			if self.reviewScoreMethod == method:
				print(f"{i+1}) {method} <---- current value")
			else:
				print(f"{i+1}) {method}")
		val=0
		while val<1 or val>len(methods):
			val=input("Which method do you want to use? ")
			try:
				val=int(val)
			except:
				val=0
		self.reviewScoreMethod=methods[val-1]
		print("Set reviewScoreMethod to " + self.reviewScoreMethod + " for " + self.name)
			
	
	def secondsPastDue(self):
		now=datetime.utcnow().replace(tzinfo=pytz.UTC)
		try:
			delta=now-self.date
			return delta.total_seconds()
		except:
			return -99999999
	
	def getDate(self, assignment):
		d=assignment.due_at_date
		try:
			for o in self.get_overrides():
				do=o.due_at_date
				if (do>d):
					d=do
		except AttributeError:
			pass
		return d
		
	def calibrate():
		return
		
	def comments():
		return "this is a comment"
		
	def creation_grade(students):		
		return 0
	
	def review_grade():
		return 0
	
	def grade(self, students):
		return 0
				
	def countPeerReviews(self):
		peer_reviews=self.get_peer_reviews()
		cnt=0		
		for peer_review in peer_reviews:
			cnt+=1
		return cnt
		
	#points defined by the criteria rubric	
	def criteria_points(self, cid):
		for criteria in self.rubric:
			if "id" in criteria:
				if criteria['id'] == cid:
					return criteria['points']
			else:
				if cid == None:
					return criteria['points']
		return 0

	#points that the score should be scaled to for grading
	def setPoints(self, defaults={}):
		print("Set an override to the defaul points on " + self.name + ":\n")
		for criteria in self.rubric:
			cid=criteria['id']
			defaultVal=self.criteria_points(cid)
			if cid in self.multiplier:
				defaultVal=self.multiplier[cid]
			elif cid in defaults:
				defaultVal=defaults[cid]
			val=input("How many points (out of 100) for '" + criteria['description'] + "' criteria [" +str(defaultVal)+ "]? ")
			try:
				val=float(val)
			except:
				val=defaultVal
			self.multiplier[cid]=val

	def pointsForCid(self, cid):
		if cid in self.multiplier:
			return self.multiplier[cid]
		return "default"	
			
	def criteria_ids(self):
		cids=[]
		for criteria in self.rubric:
			try:
				cids.append(criteria['id'])
			except:
				cids.append(None)
		return cids
		
		