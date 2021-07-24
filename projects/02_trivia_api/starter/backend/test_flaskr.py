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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '123456', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'category': 2,
            'difficulty': 2
        }


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
        self.assertEqual(data['success'], True)
        self.assertTrue(data['Categories'])
        self.assertTrue(data['total Categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['Questions'])
        self.assertTrue(data['total_Questions'])
        self.assertTrue(data['Current_category'])
        
        

        
    def test_pagenation(self):
        res= self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['Questions'])
        self.assertTrue(len(data['Questions']))


    def test_404_valid_page(self):
        res= self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


    def test_delete_question(self):
        res= self.client().delete('/questions/22')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue('Questions')
        self.assertTrue(data['total Questions'])

    def test_422_if_question_not_exit(self):
        res= self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity error')

    def test_add_question(self):
        new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1,
        }
        res= self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['Created'])
        self.assertTrue('total Questions')

    def test_422_if_add_question_not_allowed(self):
        new_question = {}
        res= self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity error')

    def test_get_search_question(self):
        res= self.client().post('/questions/search', json={'search_term':'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_Questions'])
        self.assertTrue(len(data['Questions']))

    def test_404_if_search_question_not_found(self):
        res= self.client().post('/questions/search', json={'searchTerm': 'hhhhhhh'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')   

    def test_get_question_by_category(self):
        res= self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_Questions'])
        self.assertTrue(len(data['Questions']))

    def test_422_if_get_question_by_category_not_found(self):
        res= self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity error')

    def test_play_quizz(self):
        data= {
            'previous_questions': [2, 4],
            'category': {
                'type': 'Science',
                'id': 1
            }
        }

        res= self.client().post('/quizzes', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['Questions']))

    def test_404_if_play_quizz_not_found(self):
        res= self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
