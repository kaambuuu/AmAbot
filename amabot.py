import login
import submission
import post_comment
from datetime import date
import datetime
import praw
import csv
import time

ignore_title_words = ["[AMA Request]", " [AMA request]"]

def begin():
	r_session = login.botLoginSession("down.txt")

	while 1:
		tracking = []
		try:
			tracked_amas = open("amas.txt", "r")
			tracked_amas_csv = csv.reader(tracked_amas)
		except IOError:
			tracked_amas = None
			tracked_amas_csv = []


    	#tracked_ama_csv format:
    	# [ submission_id, our_comment_permalink, last_check_year, last_check_month, last_check_day, last_check_hr, last_check_min, refresh_cnt, comments_cnt]

		ama_subreddit = r_session.session.get_subreddit('IAmA')

		for row in tracked_amas_csv:
			sub_id = row[0]
			comment_item = row[1]
			last_checked_time = datetime.datetime(year=int(row[2]), month=int(row[3]), day=int(row[4]), hour=int(row[5]), minute=int(row[6]))
			refresh_cnt = int(row[7])
			comments_cnt = int(row[8])
			new_item = submission.IamA(sub_id, last_checked_time, refresh_cnt, r_session.session, r_session.username) 
			new_commenter = post_comment.comment(str(comment_item), comments_cnt, r_session.session, sub_id, r_session.username) 
			tracking.append([sub_id, new_item, new_commenter])
		if tracked_amas != None:
			tracked_amas.close()

		for item in ama_subreddit.get_new(limit=3):
			#TODO: Check if submission title has "[Request]"
			ignore = 0
			for words in ignore_title_words:
				if words in item.title:
					print item.title
					ignore = 1
					continue
			if ignore == 1:
				continue
			#TODO: Check if submission is more than 30*max_refresh_count mins old
			timestamp = datetime.datetime.fromtimestamp(int(item.created))
			now = datetime.datetime.utcnow()
			diff = now - timestamp
			age_mins = diff.seconds/(60)
			print item.id, age_mins
			if age_mins > (6*30):  #Ignore older than 3 hrs
				print "Too old, dropping"
				continue

			not_tracked = 1
			for tracked_ama in tracking:
				if item.id == tracked_ama[0]:
					print "matched item %s" %item.id
					not_tracked = 0

			if not_tracked == 1:
				#Start tracking this
				new_item = submission.IamA(item.id, datetime.datetime.now() - datetime.timedelta(minutes=45), 0, r_session.session, r_session.username)
				new_commenter = post_comment.comment("", 0, r_session.session, item.id, r_session.username) 
				tracking.append([item.id, new_item, new_commenter])

		for item in tracking:
			print item[0]

		#All tracked items are now ready. Begin processing
		now = datetime.datetime.now()
		for item in tracking:
			submssn = item[1]
			commenter = item[2]
			if 1 == submssn.ama_update_now(now):
				if 1 == submssn.refresh_ama_replies():
					tracking.remove(item)
					continue
				text = submssn.ama_gen_conv_text()
				comment_attempt = 0
				#print "%s" %text
				while comment_attempt < 10:
					try:
						commenter.add_comments(text)
						break
					except:
						comment_attempt += 1
						print "Comment submission failed. Try %d" %comment_attempt
						time.sleep(60)
				

		#Savepoint!
		savefile = open("amas.txt", "w")
		for item in tracking:
			submssn = item[1]
			new_commenter = item[2]
			savefile.write("%s,%s,%04d,%02d,%02d,%02d,%02d,%d,%d\n" %(submssn.sub_id, new_commenter.permalink, submssn.last_check.year, submssn.last_check.month, submssn.last_check.day, submssn.last_check.hour, submssn.last_check.minute,submssn.refresh_count, new_commenter.partscnt))
		savefile.close()
		time.sleep(120)
		








