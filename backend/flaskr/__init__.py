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
  
  CORS(app)


  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
    return response


  @app.route('/categories')
  def get_categories():
    return jsonify({
        "categories": {c.id:c.type for c in Category.query.all()} 
    })


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


  @app.route('/questions', methods=['POST'])
  def post_questions():
    data = request.get_json()

    if "searchTerm" in data:
      return get_search_questions(data["searchTerm"])
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


  def get_search_questions(search_term):
    questions = [
            q.format() for q
            in Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    ]

    return jsonify({
        "questions": questions,
        "total_questions": Question.query.count()
    })


  @app.route('/categories/<int:category_id>/questions')
  def get_questions_per_category(category_id):
    category = Category.query.get_or_404(category_id)

    questions = [
            q.format() for q
            in Question.query.filter(Question.category==category.id).all()
    ]

    return jsonify({
        "questions": questions,
        "total_questions": len(questions),
        "current_category": category.id
    })


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

    
