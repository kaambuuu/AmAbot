import csv
import praw
import datetime

class IamA:
	max_search_depth = 15
	max_refreshes = 7
	delay_between_updates_mins = 30
	max_comment_len = 9500
	def __init__(self, sub_id, last_check, refresh_count, session, username):
		self.sub_id = sub_id
		self.last_check = last_check
		self.refresh_count = refresh_count
		self.session = session
		self.tracked_replies = []
		self.tracked_usernames = []
		self.nextupdate = self.last_check  + datetime.timedelta(minutes=self.delay_between_updates_mins)
		self.username = username #do not record these
		return

	def username_to_redditor(self, username):
		return self.session.get_redditor(user_name=username)

	def refresh_ama_replies(self):
		self.tracked_replies = []
		submission = self.session.get_submission(submission_id = self.sub_id)
		print "getting all comments"
		submission.replace_more_comments(limit=5,threshold=100)
		print "100s done"
		submission.replace_more_comments(limit=500,threshold=10)
		print "10s done"
		submission.replace_more_comments(limit=None,threshold=1)
		print "obtained all comments"
		self.tracked_usernames.append(submission.author.name)

		comments = submission.comments
		#print comments
		for item in comments:
#			print "New comment"
			if not item.author:
				continue #catch deleted user
			if(item.author.name == self.username):
				print "Skipping"
			else:
				self.scan_forest(item, [], 0)
		self.last_check = datetime.datetime.now()
		self.nextupdate = self.last_check + datetime.timedelta(minutes=self.delay_between_updates_mins)
		self.refresh_count += 1

		if self.refresh_count > self.max_refreshes:
			return 1 #end of AMA

		return 0

	def record_path(self, string_item, comment):
#		print "item added"
		timestamp = datetime.datetime.fromtimestamp(int(comment.created))
		string_item.append("\n\n %02d-%02d-%04d %02d:%02d  [Link](%s)" %(timestamp.month, timestamp.day, timestamp.year, timestamp.hour, timestamp.minute, comment.permalink))
		self.tracked_replies.append(string_item)

	def scan_forest(self, comment, path, depth):
		author_tracked = 0
		if not comment.author:
			return 0 #catch deleted user
		comment_auth = comment.author.name
#		print comment_auth
		if comment_auth in self.tracked_usernames:
#			print "MATCH!!!"
			author_tracked = 1
		mypath = []
		mypath += path
		const_string = "\n/u/" + comment.author.name + " \n\n" + comment.body
		mypath.append(const_string)

		if(depth > self.max_search_depth):
			if(author_tracked == 1):
				self.record_path(path, comment)
			return author_tracked

		if comment.replies == []:
			#No more comments
			if author_tracked == 1:
				self.record_path(mypath, comment)
			return author_tracked
		else:
			#We have replies. Parse them
			found_in = 0
			for reply in comment.replies:
				found_more = self.scan_forest(reply, mypath, depth + 1)
				if found_more == 1:
					found_in = 1 #We found a record deeper in. Don't record this position
			if found_in == 0:
				#None found inside. 
				if author_tracked == 1:
					#But we still need to be recorded
					self.record_path(mypath, comment)
					found_in = 1 #We found one at this level
			return found_in

	def ama_gen_conv_text(self):
		all_parts = []
		conv_text = "\n\n*IamA Summary*\n\n--------------------\n\n"
		for comment_thread in self.tracked_replies:
			curr_entry = ""
			for msg in comment_thread:
				curr_entry += msg + "\n"
			if len(conv_text) + len(curr_entry) + 50 > self.max_comment_len:
				conv_text += "\n\nI am  A Bot. v0.01. Warning: This bot is *very* buggy. Under care of /u/downvotesattractor."
				if self.refresh_count < self.max_refreshes:
					conv_text += " \n\n If bot is alive, next update will be attempted around %02d:%02d PST" %(self.nextupdate.hour, self.nextupdate.minute)
				else:
					conv_text += " \n\n There will be no further updates here"	
				all_parts.append(conv_text)
				conv_text = ""
			conv_text += curr_entry + "\n"
			conv_text += "\n\n---------------\n\n"

		conv_text += "\n\nI am  A Bot. v0.01. Warning: This bot is *very* buggy. Under care of /u/downvotesattractor."
		if self.refresh_count < self.max_refreshes:
			conv_text += " \n\n If bot is alive, next update will be attempted around %02d:%02d PST" %(self.nextupdate.hour, self.nextupdate.minute)
		else:
			conv_text += " \n\n There will be no further updates here"	

		all_parts.append(conv_text)
		return all_parts

	def ama_update_now(self, timestamp):
		if(timestamp > self.nextupdate):
			return 1
		else:
			return 0








