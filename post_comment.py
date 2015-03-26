import praw
import time

class comment:
	def __init__(self, permalink, partscnt, session, sub_id, username):
		self.permalink = permalink
		self.partscnt = partscnt
		self.session = session
		self.sub_id = sub_id
		self.botname = username

		#get parent comment
		if partscnt > 0:
			fake_submission = self.session.get_submission(self.permalink)
			self.parent_comment = fake_submission.comments[0]
		else:
			self.parent_comment = None
		return

	def add_comments(self, text_parts):
		reply_to = self.parent_comment
		for item in text_parts:
			print "Part %d" %text_parts.index(item)
			raw_text = ""
			if(len(text_parts) > 1):
				raw_text += "Part %d of %d\n\n" %((text_parts.index(item) + 1), len(text_parts))
			raw_text += item
			if self.parent_comment == None:
				#First time adding a comment
				print "New Comment"
				submission = self.session.get_submission(submission_id=self.sub_id)
				self.parent_comment = submission.add_comment(raw_text)
				reply_to = self.parent_comment
				self.parent_comment.refresh()
				self.permalink = self.parent_comment.permalink
			else:
				if(text_parts.index(item) == 0):
					#Edit parent comment
					print "Edited L0"
					self.parent_comment = self.parent_comment.edit(raw_text)
					fake_submission = self.session.get_submission(self.permalink)
					self.parent_comment = fake_submission.comments[0]
					self.parent_comment.refresh()
				else:
					#Recursively go to required depth and edit or add
					print "Searching Recursively"
					reply_to = self.add_or_edit(raw_text, self.parent_comment, text_parts.index(item), 0) 
					fake_submission = self.session.get_submission(self.permalink)
					self.parent_comment = fake_submission.comments[0]
					self.parent_comment.refresh()
		self.partscnt = len(text_parts)

	def add_or_edit(self, text, comment, depth, curr_depth):
		print "Depth %d, curr %d" %(depth, curr_depth)
		if(depth == curr_depth + 1):
			#Replies to current level are at required depth. Edit it or create it
			replies = comment.replies
			for item in replies:
				if item.author:
					if item.author.name == self.botname:
						#We have commented at this depth.
						#edit it
						print "Editing Text here"
						return item.edit(text)
			#No deeper replies were found. Add our reply (create a new reply)
			print "Adding reply here"
			return comment.reply(text)
		else:
			#Go deeper
			replies = comment.replies
			for item in replies:
				if item.author:
					if item.author.name == self.botname:
						print "Going deeper"
						self.add_or_edit(text, item, depth, curr_depth + 1)









