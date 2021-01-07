import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import seed, choice

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def get_paginated_questions(page_number):
  start_index = (page_number - 1) * QUESTIONS_PER_PAGE
  end_index = start_index + QUESTIONS_PER_PAGE
  questions_page = Question.query.order_by(Question.id).slice(start_index, end_index)
  return [q.format() for q in questions_page]


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  seed()
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    return jsonify({
        "categories": {c.id:c.type for c in Category.query.all()} 
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
  @app.route('/questions')
  def get_questions():
    page_number = request.args.get('page', 1, type=int)
    questions = get_paginated_questions(page_number)

    if len(questions) == 0:
      abort(404)

    return jsonify({
        "questions": questions,
        "total_questions": Question.query.count(),
        "categories": {c.id:c.type for c in Category.query.all()},
        "current_category": None
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    question = Question.query.get_or_404(question_id)

    try:
      question.delete()
      questions = get_paginated_questions(1)
      total_questions = Question.query.count()

      return jsonify({
          "deleted": question_id,
          "questions": questions,
          "total_questions": total_questions
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
  @app.route('/questions', methods=['POST'])
  def post_questions():
    data = request.get_json()

    if "search" in data:
      return get_search_questions(data["search"])
    else:
      return insert_question(data)

  
  def insert_question(data):
    data = request.get_json()

    try:
      new_question = Question(
              question=data['question'],
              answer=data['answer'],
              difficulty=data['difficulty'],
              category=data['category']
      )
      new_question.insert()

      return jsonify({
          "created": new_question.id
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
  def get_search_questions(search_term):
    questions = [
            q.format() for q
            in Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    ]

    return jsonify({
        "questions": questions,
        "total_questions": Question.query.count()
    })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_per_category(category_id):
    category = Category.query.get_or_404(category_id)

    questions = [
            q.format() for q
            in Question.query.filter(Question.category==category.id).all()
    ]

    return jsonify({
        "questions": questions,
        "total_questions": Question.query.count(),
        "current_category": category.id
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
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    data = request.get_json()

    category_id = data['quiz_category']['id']
    query = Question.query

    if category_id != 0:
      category = Category.query.get_or_404(category_id)
      query = query.filter(Question.category==category.id)

    previous_questions = data['previous_questions']
    if(len(previous_questions) > 0):
        query = query.filter(~Question.id.in_(previous_questions))

    question_selected = choice(query.all()).format() if query.count() > 0 else None

    return jsonify({"question": question_selected})


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
        "message": "The requested resource could not be found"
    }), 404  


  @app.errorhandler(422)
  def entity_not_processable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "The request was well-formed but was unable to be followed due to semantic errors"
    }), 422


  return app

    
