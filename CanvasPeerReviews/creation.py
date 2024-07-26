class Creation:
	def __init__(self, submission):
		self.__dict__ = submission.__dict__.copy()
		self.create_submission_peer_review = submission.create_submission_peer_review
		self.delete_submission_peer_review = submission.delete_submission_peer_review
		self.get_submission_peer_reviews = submission.get_submission_peer_reviews
		self.edit = submission.edit
		self.reviews = []
		self.excused = False
		self.reviewCount=0
		self.graderReviewCount=0
		self.secondPassReviewerIds=[]
		
	def assignedPeerReviews(self):
		returnList=[]
		for peer_review in self.get_submission_peer_reviews():
			returnList.append(peer_review)
		return returnList