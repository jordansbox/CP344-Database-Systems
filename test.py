# to run this test, execute the command "python3 -m unittest -v <this file>"
import pprint, random, string, unittest
import qanda, qanda_impl

emails = [ "qu_1@gmail.com", "qu_2@icloud.com", "qu_3@yahoo.com", "qu_4@msn.com" ]
n_emails = len( emails )

lines = open("sonnet_snippets.txt").read().splitlines()

def random_text( ):
  # generate a random string from printable characters that is between 10 and 255
  # characters long
  return lines[ random.randint( 0, len( lines ) - 1 ) ]

class TestQandA( unittest.TestCase ):
  
  # setUp will be called by the test framework before every test
  def setUp ( self ):
    self.qanda = qanda_impl.QandA_Impl( )
    self.user_entity = self.qanda.user_entity( )
    self.question_entity = self.qanda.question_entity( )
    self.answer_entity = self.qanda.answer_entity( )
    pass

  # setUp will be called by the test framework after every test
  def tearDown( self ):
    pass

  # each test must be self-contained and cannot depend on another
  # tests are executed in lexical order
  def test_01_initialize( self ):
    self.qanda.initialize( )
    users = self.user_entity.get_all( )
    questions = self.question_entity.get_all( )
    answers = self.answer_entity.get_all( )
    # confirm the database is empty
    self.assertEqual( len( users ), 0 )
    self.assertEqual( len( questions ), 0 )
    self.assertEqual( len( answers ), 0 )
    
  def test_02_adduser( self ):
    # add users
    uids = [ self.user_entity.new( email ) for email in emails ]
    # assert the ids returned have no duplicates
    self.assertEqual( len( set( uids ) ), len( uids ) )
    # assert the number of users is as expected
    self.assertEqual( len( uids ), n_emails )
    # adding the same user should result in an exception
    try:
      self.user_entity.new( emails[0] )
      self.fail( "able to add the same user twice" )
    except KeyError:
      pass
    
  def test_03_askquestion( self ):
    # have each user pose a question
    users = self.user_entity.get_all( )
    self.assertEqual( len( users ), n_emails )
    qids = [ self.question_entity.new( user.id, random_text( ) ) for user in users ]
    # number of questions should match number of users
    self.assertEqual( len( qids ), len( users ) )
    
  def test_04_answer( self ):
    # have each user answer a random question
    users = self.user_entity.get_all( )
    questions = self.question_entity.get_all( )
    self.assertEqual( len( questions ), n_emails )
    choices = random.sample( range( n_emails ), n_emails )
    givens = []
    for i in range( n_emails ):
      q = questions[ choices[ i ] ]
      text = random_text( )
      self.answer_entity.new( users[ i ].id, q.id, text )
      givens.append( text )
      
    # number of answers should match number of users
    answers = self.answer_entity.get_all( )
    self.assertEqual( len( answers ), n_emails )
    # confirm the answers match what are provided earlier
    texts = [ answer.text for answer in answers ]
    self.assertTrue( sorted( texts ) == sorted( givens ) )
    
    # assert total number of votes is zero
    all_votes = sum( [ answer.up_vote + answer.down_vote for answer in answers ] )
    self.assertEqual( all_votes, 0 )
        
  def test_05_vote( self ):
    # have each user vote 'up' on the other questions
    # assert total number of up votes matches number of votes cast
    answers = self.answer_entity.get_all( )
    users = self.user_entity.get_all( )
    for user in users:
      for answer in answers:
        self.answer_entity.vote( user.id, answer.id, qanda.Vote.Up )
    n_vote = len( users ) * len( answers )
    answers = self.answer_entity.get_all( )
    self.assertEqual( sum( [ answer.up_vote for answer in answers ] ), n_vote )
    self.assertEqual( sum( [ answer.down_vote for answer in answers ] ), 0 )
    
  def test_06_del_user( self ):
    # delete all the users
    users = self.user_entity.get_all( )
    answers = self.answer_entity.get_all( )
    questions = self.question_entity.get_all( )
    [ self.user_entity.delete( user.id ) for user in users ]
    # verify users are gone
    users = self.user_entity.get_all( )
    self.assertEqual( len( users ), 0 )
    
    # verify the questions and answers remain unchanged by user deletion
    answers_2 = self.answer_entity.get_all( )
    questions_2 = self.question_entity.get_all( )
    aid = [ answer.id for answer in answers ]
    aid_2 = [ answer.id for answer in answers_2 ]
    self.assertEqual( sorted( aid ), sorted( aid_2 ) )
    qid = [ q.id for q in questions ]
    qid_2 = [ q.id for q in questions_2 ]
    self.assertEqual( sorted( qid ), sorted( qid_2 ) )
    
  def test_07_del_question( self ):
    # find a question with answers
    questions = self.question_entity.get_all( )
    for q in questions:
      answers = self.answer_entity.get_answers( q.id )
      if len( answers ) > 0:
        qid = q.id
        aid = answers[ 0 ].id
        break
    # if no question is found, use of qid or aid will trigger an exception here
    self.question_entity.delete( qid )
    try:
      # verify answers to a deleted question are deleted as well
      self.answer_entity.get( aid )
      self.fail( "answer not deleted while question is deleted" )
    except KeyError:
      pass

  def test_08_question_neg( self ):
    # simple negative tests for questions
    msg = "0 should not be a valid id"
    try:
      self.question_entity.get( "0" )
      self.fail( msg )
    except KeyError:
      pass
    try:
      self.question_entity.new( "0", "abcde" )
      self.fail( msg )
    except KeyError:
      pass
    try:
      self.question_entity.delete( "0" )
      self.fail( msg )
    except KeyError:
      pass
      
  def test_09_answer_neg( self ):
    # simple negative tests for answers
    msg = "0 should not be a valid id"
    try:
      self.answer_entity.get( "0" )
      self.fail( msg )
    except KeyError:
      pass
    try:
      self.answer_entity.new( "0", "0", "abcde" )
      self.fail( msg )
    except KeyError:
      pass
    try:
      self.answer_entity.vote( "0", "0", qanda.Vote.Down )
      self.fail( msg )
    except KeyError:
      pass
    try:
      self.answer_entity.delete( "0" )
      self.fail( msg )
    except KeyError:
      pass

unittest.main()