class Review:
	def __init__(self, review_type, reviewer_id, author_id, assignment_id, submission_id, data):
		self.review_type=review_type
		self.reviewer_id = reviewer_id
		self.author_id = author_id
		self.assignment_id = assignment_id
		self.submission_id = submission_id
		self.excused = False		
		self.data = data
		self.scores=dict()
		for s in self.data:
			try:
				self.scores[s['criterion_id']]=s['points']
			except:
				err="Unscored criteria"
				
	def disp(self):
		msg = "(" + str(self.reviewer_id) + ") review of submission by (" + str(self.author_id) + "): "
		msg += "["
		for s in self.data:
			try:
				msg+="Criteria" +str(s['criterion_id']) + " " + str(s['points'])+", "
			except:
				msg+="Criteria" +str(s['criterion_id']) + " " + "---, "
		msg=msg[0:-2]+ "]"			
		return msg
		
	def fingerprint(self):
		return "assignment_id=" + str(self.assignment_id) + "&author_id=" + str(self.author_id) + "&reviewer_id="+str(self.reviewer_id)