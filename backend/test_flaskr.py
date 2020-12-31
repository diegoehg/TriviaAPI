import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

def init_categories(db):
    if Category.query.count() == 0:
        c = Category(type='Science')
        db.session.add(c)
        c = Category(type='Art')
        db.session.add(c)
        c = Category(type='Geography')
        db.session.add(c)
        c = Category(type='History')
        db.session.add(c)
        c = Category(type='Entertainment')
        db.session.add(c)
        c = Category(type='Sports')
        db.session.add(c)
        db.session.commit()


def init_questions():
    if Question.query.count() == 0:
        q = Question(question="Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?", answer="Maya Angelou", difficulty=2, category=4)
        q.insert()
        q = Question(question="What boxer's original name is Cassius Clay?", answer="Muhammad Ali", difficulty=1, category=4)
        q.insert()
        q = Question(question="What movie earned Tom Hanks his third straight Oscar nomination, in 1996?", answer="Apollo 13", difficulty=4, category=5)
        q.insert()
        q = Question(question="What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?", answer="Tom Cruise", difficulty=4, category=5)
        q.insert()
        q = Question(question="What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?", answer="Edward Scissorhands", difficulty=3, category=5)
        q.insert()
        q = Question(question="Which is the only team to play in every soccer World Cup tournament?", answer="Brazil", difficulty=3, category=6)
        q.insert()
        q = Question(question="Which country won the first ever soccer World Cup in 1930?", answer="Uruguay", difficulty=4, category=6)
        q.insert()
        q = Question(question="Who invented Peanut Butter?", answer="George Washington Carver", difficulty=2, category=4)
        q.insert()
        q = Question(question="What is the largest lake in Africa?", answer="Lake Victoria", difficulty=2, category=3)
        q.insert()
        q = Question(question="In which royal palace would you find the Hall of Mirrors?", answer="The Palace of Versailles", difficulty=3, category=3)
        q.insert()
        q = Question(question="The Taj Mahal is located in which Indian city?", answer="Agra", difficulty=2, category=3)
        q.insert()
        q = Question(question="Which Dutch graphic artist–initials M C was a creator of optical illusions?", answer="Escher", difficulty=1, category=2)
        q.insert()
        q = Question(question="La Giaconda is better known as what?", answer="Mona Lisa", difficulty=3, category=2)
        q.insert()
        q = Question(question="How many paintings did Van Gogh sell in his lifetime?", answer="One", difficulty=4, category=2)
        q.insert()
        q = Question(question="Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?", answer="Jackson Pollock", difficulty=2, category=2)
        q.insert()
        q = Question(question="What is the heaviest organ in the human body?", answer="The Liver", difficulty=4, category=1)
        q.insert()
        q = Question(question="Who discovered penicillin?", answer="Alexander Fleming", difficulty=3, category=1)
        q.insert()
        q = Question(question="Hematology is a branch of medicine involving the study of what?", answer="Blood", difficulty=4, category=1)
        q.insert()
        q = Question(question="Which dung beetle was worshipped by the ancient Egyptians?", answer="Scarab", difficulty=4, category=4)
        q.insert()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_dialect = "sqlite"
        self.database_location = ""
        self.database_name = "trivia_test.db"
        self.database_path = f"{self.database_dialect}://{self.database_location}/{self.database_name}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            init_categories(self.db)
            init_questions()
    
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

        data_expected = [c.format() for c in Category.query.all()]
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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
