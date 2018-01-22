from py2neo import Graph, Node, Relationship
from datetime import datetime
import uuid
import os

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')


class User:
	users_db = {}
	posts = []
	
	def __init__(self, name):
		self.username = name
				
	def find(self):
		try:
			return self.users_db[self.username]
		except:
			return None
	
	def register(self, password):
		if not self.find():
			self.users_db[self.username] = password				
			return True
		else:
			return False
		
	def verify_password(self, password):
		_password = self.find()
		if _password:
			return _password == password
			
	def add_post(self, title, tags, text):		
		self.posts.append(
			{'username':self.username, 
			 'post':{'title':title, 'date':'20-1-2018', 'text':text},
			 'tags':[x.strip() for x in tags.lower().split(',')]
			}
		)		
				
	def get_recent_posts(self):
		return [post for post in self.posts if post['username'] == self.username]
						

def get_todays_recent_posts():
	return [
	{'username':'james', 
		'post': {'title':'t1', 'date':'20-1-2017','text':'hello world'}, 
		'tags':['power', 'theshit']},

	{'username':'becky', 
		'post': {'title':'t2', 'date':'20-1-2017','text':'hello to you too'}, 
		'tags':['power']}
	]	
