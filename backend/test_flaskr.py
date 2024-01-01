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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_delete_question(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 10).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], 10)
        self.assertTrue(data['success'])
        self.assertEqual(question, None)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        res = self.client().post('/questions', json={
            'question': 'Test question',
            'answer': 'Test answer',
            'difficulty': 1,
            'category': 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])

    def test_422_create_question(self):
        res = self.client().post('/questions', json={
            'question': 'Test question',
            'answer': 'Test answer',
            'difficulty': 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={
            'searchTerm': 'Test'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_422_search_questions(self):
        res = self.client().post('/questions/search', json={
            'searchTerm': None
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Science')

    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [23, 12],
            'quiz_category': {
                'id': 4
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_404_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [23, 12],
            'quiz_category': {
                'id': 10000
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_422_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': None,
            'quiz_category': {
                'id': None
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()