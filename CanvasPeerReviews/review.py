class Review:
	def __init__(self, assessment, creation):
		self.review_type=assessment['assessment_type']
		self.reviewer_id = assessment['assessor_id']
		self.author_id = creation.user_id
		self.assignment_id = creation.assignment_id
		self.submission_id = assessment['artifact_id']
		self.id=assessment['id']
		self.excused = False		
		self.data = assessment['data']
		self.scores=dict()
		self.comments=dict()
		for s in self.data:
			try:
				self.scores[s['criterion_id']]=s['points']
				self.comments[s['criterion_id']]=s['comments']
			except:
				err="Unscored criteria"
		ce=creation.edit()
		self.comments[0]="\n\n".join([comment_item['comment'] for comment_item in ce.submission_comments if comment_item['author_id']==self.reviewer_id])
		self.allComments="\n".join(self.comments.values())
		self.commented=len(self.allComments)>2
				
				
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