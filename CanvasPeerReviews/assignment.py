class GradedAssignment:
	def __init__(self, assignment):	
		if hasattr(assignment, 'rubric'):
			for outcome in assignment.rubric:
				if not 'id' in outcome:
					outcome['id']=None
		self.__dict__ = assignment.__dict__.copy() 
		self.graded = False 
		self.regraded = False 
		self.peer_reviews_assigned = False
		self.get_peer_reviews=assignment.get_peer_reviews
		self.get_submissions=assignment.get_submissions

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
		
	def criteria_points(self, cid):
		for criteria in self.rubric:
			if "id" in criteria:
				if criteria['id'] == cid:
					return criteria['points']
			else:
				if cid == None:
					return criteria['points']
		return 0
			
	def criteria_ids(self):
		cids=[]
		for criteria in self.rubric:
			try:
				cids.append(criteria['id'])
			except:
				cids.append(None)
		return cids