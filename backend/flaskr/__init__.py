import os
from flask import Flask, request, abort, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# pagination function for questions
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  # Endpoint to Get all available categories
  @app.route('/categories', methods=['GET'])
  def available_categories():
     categories = Category.query.all()
     formated_category = [category.format() for category in categories]

     if len(formated_category) == 0:
       return abort(404)
       
     else:
      return jsonify({
        'success' : True,
        'categories' : formated_category,
        'total categories' : len(formated_category)
      })

  # Endpoint Get specific category
  @app.route('/categories/<int:category_id>', methods=['GET'])
  def specific_category(category_id):
     category = Category.query.filter(Category.id == category_id).one_or_none()

     if category == None:
       return abort(404)
     else:
       return jsonify({
         'success' : True,
         'category' : category.format()
       })

  
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  # Endpoint to show questions --> 10 per page 
  @app.route('/pages/<int:page_num>/questions', methods=['GET'])
  def get_questions(page_num):

    total_questions = Question.query.all()
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.all()
    current_categories = [category.type.format() for category in categories]
    # here to check and don't show pages out of range of total pages available
    total_pages = int(len(selection) / len(current_questions))
    if page_num in range(1, (total_pages + 1)):

      if len(current_questions) == 0:
        return abort(404)
      
      else:
        return jsonify({
        'Questions' : current_questions,
        'Questions per page' : len(current_questions),
        'Total questions' : len(total_questions),
        'Total pages' : total_pages,
        'current categories' : current_categories,
        'success' : True
      })
    else: 
      abort(404)
  # Endpoint to Get specific question
  @app.route('/questions/<int:question_id>', methods=['GET'])
  def show_specific_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question == None:
      return abort(404)
    else:
      return jsonify({
        'success' : True,
        'Question' : question.format()
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  # Endpoint to Delete Questions based on question id
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question == None:
        abort(404)
      else:
        question.delete()
        return jsonify({
          'success' : True,
          'deleted question' : question_id,
          'questions' : len(Question.query.all())
        })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  # Endpoint to Post new Questions
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    
    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      return jsonify({
        'success' : True,
        'The new question' : question.format(),
        'total questions' : len(Question.query.all())
      })
    
    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search/<string:search_term>', methods=['GET','POST'])
  def search(search_term):
     result = Question.query.filter(Question.question.ilike(search_term + '%')).all()
     formated_questions = [question.format() for question in result]

     if formated_questions == []: 
       return abort(404)

     else:
       return jsonify({
         'success' : True,
         'results' : formated_questions,
         'number of result found' : len(formated_questions)
       })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_type>/questions/', methods=['GET'])
  def question_based_on_category(category_type):
     questions = Question.query.order_by(Question.category == category_type).all()
     formated_questions = [question.format() for question in questions]

     if category_type == None:
       return abort(404)
     else:
       return jsonify({
         'success' : True,
         'category' : formated_questions
       })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['GET','POST'])
  def post_quiz():

    try:

      # if the the request method is GET 
      if request.method == 'GET':

        questions = Question.query.order_by(Question.category).all()

      # if the the request method is POST
      elif request.method == 'POST':

        body = request.get_json()
        quiz_categoy = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        questions = Question.query.filter(Question.category == quiz_categoy).all()

      total_questions = len(questions)

      previous_questions = []
      quiz = []
      quiz_len = len(quiz)

      while int(len(quiz)) < total_questions:
        question = random.choice(questions).format()

        # condition to check if the next questions in previous questions list 
        if question not in previous_questions:
          previous_questions.append(question)
          quiz.append(question)

      return jsonify({
        'success' : True,
        'total_questions': len(quiz),
        'questions' : quiz
      })
   
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success' : False,
      'error' : 400,
      'message' : "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success' : False,
      'error' : 404,
      'message' : "resource not found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      'success' : False,
      'error' : 405,
      'message' : "method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error' : 422,
      'message' : "unprocessable"
    }), 422
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success' : False,
      'error' : 500,
      'message' : "Internal Server Error"
    }), 

  return app

    