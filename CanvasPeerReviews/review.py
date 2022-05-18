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
				self.scores[s['learning_outcome_id']]=s['points']
			except:
				err="Unscored LO"
				
	def disp(self):
		msg = "(" + str(self.reviewer_id) + ") review of submission by (" + str(self.author_id) + "): "
		msg += "["
		for s in self.data:
			try:
				msg+="LO_" +str(s['learning_outcome_id']) + " " + str(s['points'])+", "
			except:
				msg+="LO_" +str(s['learning_outcome_id']) + " " + "---, "
		msg=msg[0:-2]+ "]"			
		return msg
