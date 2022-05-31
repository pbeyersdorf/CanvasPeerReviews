class GradedAssignment:
	def __init__(self, assignment):	
		if hasattr(assignment, 'rubric'):
			for outcome in assignment.rubric:
				if not 'id' in outcome:
					outcome['id']=None
		self.__dict__ = assignment.__dict__.copy() 
		self.graded = False 
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
		
	def learning_outcome_points(self, LOid):
		for outcome in self.rubric:
			if "id" in outcome:
				if outcome['id'] == LOid:
					return outcome['points']
			else:
				if LOid == None:
					return outcome['points']
		return 0
			
	def learning_outcome_ids(self):
		LOids=[]
		for outcome in self.rubric:
			try:
				LOids.append(outcome['id'])
			except:
				LOids.append(None)
		return LOids