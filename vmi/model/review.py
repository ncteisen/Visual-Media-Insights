class Review:
	def __init__(self, title, body):
		# title of the review
		self.title = title
		#  body of the review.
		self.body = body

	def __str__(self):
		return "{title}\n\n{body}".format(title=self.title, body=self.body)