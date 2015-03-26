#login.py
import csv
import praw
from datetime import date

class botLoginSession:
    def __init__(self, loginFile):
        try:
            loginDetails = open(loginFile, 'r')
        except IOError:
            self.error = 3
            return 
        loginCSV = csv.reader(loginDetails)
        for row in loginCSV:
            if row == []:
                break
            if row[0] == "username":
                self.username = row[1]
            if row[0] == "passwd":
                self.password = row[1]
            if row[0] == "user agent":
                self.user_agent = row[1]
        
        self.session = praw.Reddit(user_agent = self.user_agent)
        try:
            self.session.login(self.username, self.password)
        except praw.errors.InvalidUserPass:
            self.error = 2
            return #BOT_BADUSERNAME
        self.timestamp = date.today() 
        self.error = 0
        return 












