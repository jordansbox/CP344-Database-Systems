import sqlite3, qanda

conn = sqlite3.connect('qanda.db')
c=conn.cursor()
inc=0

class QandA_Impl(qanda.QandA):
	def initialize(self):
		c.execute('DELETE FROM User')
		c.execute('DELETE FROM Question')
		c.execute('DELETE FROM Answer')

	def user_entity(self):
		u=UserEntity()
		u.initialize()
		return u

	def question_entity(self):
		q=QuestionEntity()
		q.initialize()
		return q

	def answer_entity(self):
		a=AnswerEntity()
		a.initialize()
		return a

class UserEntity(qanda.Entity):
	def initialize(self):
		c.execute('CREATE TABLE IF NOT EXISTS User (email TEXT, passhash TEXT, PRIMARY KEY(email))')
		c.execute('DELETE FROM User')

	def get(self, id):
		t=(id,)
		c.execute('SELECT * FROM User WHERE email = ?', t)
		gotten=c.fetchone()
		return gotten

	def get_all(self):
		c.execute('SELECT * FROM User')
		arr=c.fetchall()
		return arr

	def delete(self, id):
		t=(id,)
		c.execute('DELETE FROM User WHERE email=?', t)

	def new(self, email, passhash= None):
		t=(email,)
		c.execute('SELECT * FROM User WHERE email = ?', t)
		x=(email, passhash,)
		c.execute('INSERT INTO User VALUES(?,?)', x)
		return email


class QuestionEntity(qanda.Entity):
	def initialize(self):
		c.execute('CREATE TABLE IF NOT EXISTS Question (qid INT, email TEXT, body TEXT, PRIMARY KEY(qid))')
		c.execute('DELETE FROM Question')

	def get(self, id):
		t=(id,)
		c.execute('SELECT * FROM User WHERE qid = ?', t)
		gotten=c.fetchone()
		return gotten

	def get_all(self):
		c.execute('SELECT * FROM Question WHERE qid IS NOT NULL')
		ray=c.fetchall()
		return ray

	def delete(self, qid):
		t=(qid,)
		c.execute('DELETE FROM Answer WHERE qid=?', t)
		c.execute('DELETE FROM Question WHERE qid=?', t)

	def new(self, email, text):
		t=(email,)
		inc+=1
		qid=inc
		x=(qid,email,text)
		c.execute('SELECT * FROM User WHERE email = ?', t)
		c.execute('INSERT INTO Question VALUES(?)', x)
		return qid

class AnswerEntity(qanda.Entity):
	def initialize(self):
		c.execute('CREATE TABLE IF NOT EXISTS Answer (aid INT, qid INT, email TEXT, body TEXT, up_vote INT, down_vote INT, PRIMARY KEY(aid))')
		c.execute('DELETE FROM Answer')

	def get(self, id):
		t=(id,)
		c.execute('SELECT * FROM Answer WHERE aid = ?', t)
		gotten=c.fetchone()
		return gotten


	def get_all(self):
		c.execute('SELECT * FROM Answer')
		ray=c.fetchall()
		return ray

	def delete(self, id):
		t=(id,)
		c.execute('DELETE FROM Answer WHERE aid=?', t)

	def new(self, qid, email, text):#id gen how
		t=(id,)
		c.execute('SELECT * FROM User WHERE email= ?', t)
		t=(qid,)
		c.execute('SELECT * FROM Question WHERE qid= ?', t)
		inc+=1
		aid=inc
		x=(aid, qid, email, text, 0, 0)
		c.execute('INSERT INTO Answer VALUES (?)', x)
		return aid

	def get_answers( self, id ):#looks good - need to check return format
		t=(id,)
		c.execute('SELECT * FROM Answer WHERE qid =  ?', t)
		ray=c.fetchall()
		return ray

	"""In test.py the vote parameter is treated as a number. That's nice."""
	def vote( self, email, aid, vote ):
		t=(email,)
		c.execute('SELECT * FROM User WHERE email = ?', t)
		if vote:
			t=(aid,)
			c.execute('SELECT up_vote FROM Answer WHERE aid = ?', t)
			s=c.fetchone()+1
			c.execute('UPDATE Answer SET up_vote=? WHERE aid = ?', s,t)
		else:
			t=(aid,)
			c.execute('SELECT down_vote FROM Answer WHERE aid = ?', t)
			s=c.fetchone()+1
			c.execute('UPDATE Answer SET up_vote=? WHERE aid = ?', s,t)
		"""up and down votes are returned as a pair"""
		return   