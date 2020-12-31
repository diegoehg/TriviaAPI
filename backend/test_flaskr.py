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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
