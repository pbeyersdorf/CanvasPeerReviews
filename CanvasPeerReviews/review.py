class Review:
	def __init__(self, assessment, creation):
		self.creation=creation
		self.assessment=assessment
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
		self.minimumRequiredCommentLength=2
		#reviewURL # https://sjsu.instructure.com/courses/1490126/assignments/6272805/anonymous_submissions/Yp4en
		#previewURL #https://sjsu.instructure.com/courses/1490126/assignments/6272805/submissions/4552373?preview=1&version=1
		#self.url=creation.preview_url.split("submissions/")[0] + "anonymous_submissions/"
		self.urls=[]
		try:
			for attachment in self.creation.attachments:
				previewURL=attachment['url'].split("/download")[0]
				self.urls.append(attachment['url'])
				#self.urls.append(previewURL)
		except:
			previewURL=None
			self.urls.append(None)
		self.url=self.urls[0]
		for s in self.data:
			try:
				self.scores[s['criterion_id']]=s['points']
				self.comments[s['criterion_id']]=s['comments']
			except:
				err="Unscored criteria"

	def getComments(self): # this takes a bit of time so we have it as a separate function outside the init block so that we don't have to spend the time if we don't need it.
		for s in self.data:
			try:
				self.comments[s['criterion_id']]=s['comments']
			except:
				err="Unscored criteria"
		ce=self.creation.edit()
		if (self.review_type == "grading"):
			commentToIgnore=self.creation.author.comments[self.assignment_id]
			self.commentToIgnore=commentToIgnore
			self.ce=ce
			theComments=[comment_item['comment'] for comment_item in ce.submission_comments if comment_item['author_id']==self.reviewer_id]
			theCommentsToInclude=[c for c in theComments if c!=commentToIgnore]
			self.comments[0]="\n\n".join(theCommentsToInclude)
		else:
			self.comments[0]="\n\n".join([comment_item['comment'] for comment_item in ce.submission_comments if comment_item['author_id']==self.reviewer_id])
		self.allComments="\n".join(self.comments.values()).strip()
		self.commented=len(self.allComments)>self.minimumRequiredCommentLength 
		return self.allComments
					
				
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