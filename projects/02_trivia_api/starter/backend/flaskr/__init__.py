import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagenation(request, selection):
  page= request.args.get('page',1 , type=int)
  start= (page-1) * QUESTIONS_PER_PAGE
  end= start + QUESTIONS_PER_PAGE
  Questions= [question.format() for question in selection]
  Current_Question= Questions[start:end]

  return Current_Question


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {'origins': "*"}})


 # @TODO: Use the after_request decorator to set Access-Control-Allow

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #done
  @app.route('/categories')
  def retreive_categories():
    Categories= Category.query.order_by(Category.id).all()
    Current_Category={} 

    for category in Categories:
      Current_Category[category.id] = category.type

    if len(Current_Category)==0:
      abort(404) 

    return jsonify({
      'success':True,
      'Categories':Current_Category,
      'total Categories': len(Category.query.all())
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
#done
  @app.route('/questions')
  def retreive_questions():
    Questions= Question.query.order_by(Question.id).all()
    Current_Question= pagenation(request, Questions)

    if len(Current_Question) == 0:
      abort(404)  

    Categories= Category.query.order_by(Category.id).all()
    Current_category={} 

    for category in Categories:
      Current_category[category.id] = category.type

    if len(Current_category) == 0:
      abort(404) 

    return jsonify({
      'success':True,
      'Questions':Current_Question,
      'total_Questions': len(Questions),
      'Current_category': Current_category,
      'categories': Current_category
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
#done
  @app.route('/questions/<int:questions_id>', methods=['DELETE'])
  def delete_question(questions_id):
    try:
      question= Question.query.filter(Question.id == questions_id).one_or_none()

      if question is None:
        abort(404) 

      question.delete()
      Questions= Question.query.order_by(Question.id).all()
      Current_Question= pagenation(request, Questions) 

      return jsonify({
        'success':True,
        'Delete':questions_id,
        'Questions': Current_Question,
        'total Questions': len(Questions)
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
#done
  @app.route('/questions', methods=['POST'])
  def add_new_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    if ((new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None)):
      abort(422)

    try:
      new_Question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      new_Question.insert()

      Questions= Question.query.order_by(Question.id).all()
      Current_Question= pagenation(request, Questions) 

      return jsonify({
        'success':True,
        'Created': new_Question.id,
        'question created': new_Question.question,
        'Questions': Current_Question,
        'total Questions': len(Questions)
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
#done
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body= request.get_json()
    search_term = body.get('search_term',None)

    try:
      seeking_question = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

      if seeking_question is None:
        abort(404)

      Categories= Category.query.order_by(Category.id).all()
      Current_Question= pagenation(request, seeking_question) 
      current_category = [category.format() for category in Categories]

      return jsonify({
        'success':True,
        'Questions': Current_Question,
        'current_category': current_category,
        'total_Questions': len(seeking_question)
      })

    except:
      abort(404)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
#done
  @app.route('/categories/<int:category_id>/questions')
  def questions_categories(category_id):

    try:
      category = Category.query.filter(Category.id == category_id).one_or_none()
      
      if category == None:
        abort(404)

      questions_category = Question.query.filter(Question.category == category_id).all()

      if questions_category is None:
        abort(404)

      Current_Question= pagenation(request, questions_category) 

      return jsonify({
        'success':True,
        'Questions': Current_Question,
        'Current_category': category.type,
        'total_Questions': len(questions_category)
      })

    except:
      abort(422)


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

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body= request.get_json()

    category = body.get('category', None)
    previous_question = body.get('previous_question',[])
    next_questions = []

    if category == None or previous_question == None:
      abort(404)

    try:
      if category['id'] == 0:
        quiz_question = Question.query.all()

      else:
        quiz_question = Question.query.filter(Question.category == category['id']).all()

      if len(quiz_question) == 0:
        abort(404)

      else:

        for question in quiz_question:
          if question not in previous_question:
            next_questions.append(question)

        for random_ques in next_questions:
          random_question = next_questions[random.randrange(0, len(next_questions), 1)]


        return jsonify({
          'success':True,
          'Questions': random_question.format(),
          'total Questions': len(quiz_question)
        })

    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable_entity_error(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable entity error"
    }), 422

  @app.errorhandler(400)
  def bad_request_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "Internal server error"
    }), 500


  return app

    
