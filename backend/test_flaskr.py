import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_dialect = "postgresql"
        self.database_user = "triviaapi"
        self.database_password = "triviaapi"
        self.database_location = "localhost:5432"
        self.database_name = "trivia_test"
        self.database_path = f"{self.database_dialect}://{self.database_user}:{self.database_password}@{self.database_location}/{self.database_name}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        self.assertEqual(response.status_code, 200)

        data_expected = {f'{c.id}':c.type for c in Category.query.all()}
        response_data = response.get_json()
        self.assertEqual(data_expected, response_data['categories'])


    def test_get_questions_default_page(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)
        
        questions = [q.format() for q in Question.query.order_by(Question.id).slice(0,10)]
        total_questions = Question.query.count()
        categories = {f'{c.id}':c.type for c in Category.query.all()}

        response_data = response.get_json()
        self.assertEqual(questions, response_data['questions'])
        self.assertEqual(total_questions, response_data['total_questions'])
        self.assertEqual(categories, response_data['categories'])


    def test_get_questions_page_2(self):
        response = self.client().get('/questions', query_string={'page': 2})
        self.assertEqual(response.status_code, 200)

        questions = [q.format() for q in Question.query.order_by(Question.id).slice(10,20)]
        total_questions = Question.query.count()
        categories = {f'{c.id}':c.type for c in Category.query.all()}

        response_data = response.get_json()
        self.assertEqual(questions, response_data['questions'])
        self.assertEqual(total_questions, response_data['total_questions'])
        self.assertEqual(categories, response_data['categories'])


    def test_404_when_get_questions_page_without_results(self):
        response = self.client().get('/questions', query_string={'page': 3444})
        self.assertEqual(response.status_code, 404)


    def test_delete_question(self):
        q = Question.query.first()
        question_id = q.id
        total_questions_before_delete = Question.query.count()

        response = self.client().delete(f"/questions/{question_id}")
        self.assertEqual(response.status_code, 200)

        total_questions_after_delete = Question.query.count()
        response_data = response.get_json()
        self.assertEqual(total_questions_before_delete - 1, total_questions_after_delete)
        self.assertEqual(question_id, response_data["deleted"])


    def test_404_when_deleting_non_existent_question(self):
        response = self.client().delete("/questions/88949494")
        self.assertEqual(response.status_code, 404)


    def test_post_new_question(self):
        total_questions_before_post = Question.query.count()
        new_question = {
                "question": "How is this question posted?",
                "answer": "It is posted through a REST endpoint",
                "difficulty": 1,
                "category": 1
        }

        response = self.client().post('/questions', json=new_question)
        self.assertEqual(response.status_code, 200)

        total_questions_after_post = Question.query.count()
        self.assertEqual(total_questions_before_post + 1, total_questions_after_post)

        response_data = response.get_json()
        q = Question.query.get(response_data['created'])
        self.assertEqual(new_question['question'], q.question)
        self.assertEqual(new_question['answer'], q.answer)
        self.assertEqual(new_question['difficulty'], q.difficulty)
        self.assertEqual(new_question['category'], q.category)


    def test_422_when_post_malformed(self):
        response = self.client().post(
                "/questions",
                json={
                    "oijij": 909,
                    "949494": "uksl_"
                }
        )
        self.assertEqual(response.status_code, 422)


    def test_post_search_questions(self):
        response = self.client().post(
                "/questions",
                json={"search": "which"}
        )
        self.assertEqual(response.status_code, 200)

        questions = [
                q.format() for q 
                in Question.query.filter(Question.question.ilike('%which%')).all()
        ]
        total_questions = Question.query.count()
        response_data = response.get_json()
        self.assertEqual(questions, response_data['questions'])
        self.assertEqual(total_questions, response_data['total_questions'])


    def test_422_when_posting_malformed_search(self):
        response = self.client().post(
                "/questions",
                json={"searchedseg": 495958}
        )
        self.assertEqual(response.status_code, 422)


    def test_get_questions_per_category(self):
        category = Category.query.get(2)
        response = self.client().get(f'/categories/{category.id}/questions')
        self.assertEqual(response.status_code, 200)

        questions = [
                q.format() for q
                in Question.query.filter(Question.category==category.id).all()
        ]
        total_questions = Question.query.count()

        response_data = response.get_json()
        self.assertEqual(questions, response_data['questions'])
        self.assertEqual(total_questions, response_data['total_questions'])
        self.assertEqual(category.id, response_data['current_category'])


    def test_404_category_non_existent(self):
        response = self.client().get('/categories/4556/questions')
        self.assertEqual(response.status_code, 404)


    def test_get_quiz_question_without_previous_questions(self):
        category = Category.query.get(1)

        response = self.client().post(
                '/quizzes',
                json={
                    "previous_questions": [],
                    "quiz_category": category.format()
                }
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        self.assertTrue(response_data['question'] != None)


    def test_get_quiz_question_with_previous_questions(self):
        category = Category.query.get(4)
        previous_questions = [5, 12, 23]

        response = self.client().post(
                '/quizzes',
                json={
                    "previous_questions": previous_questions,
                    "quiz_category": category.format()
                }
        )
        self.assertEqual(response.status_code, 200)

        question = response.get_json()['question']
        self.assertTrue(question != None)
        self.assertTrue(question['id'] not in previous_questions)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
