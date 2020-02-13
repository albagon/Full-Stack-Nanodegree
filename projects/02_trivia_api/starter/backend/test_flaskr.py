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
        self.database_name = 'trivia_test'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'What is the first month of the year?',
            'answer': 'January',
            'category': 1,
            'difficulty': 1
        }
        self.bad_question = {
            'question': 'Why is this question wrong?',
            'answer': 'January',
            'category': 'wrong',
            'difficulty': 1
        }
        self.search_term = {
            'searchTerm': 'title'
        }
        self.absent_term = {
            'searchTerm': 'xxx'
        }
        self.empty_term = {
            'searchTerm': ''
        }
        self.quiz = {
            'previous_questions': [{
                'id': 1,
                'question': 'What is the first month of the year?',
                'answer': 'January',
                'category': 1,
                'difficulty': 1
            }],
            'quiz_category': {
                'id': 1,
                'type': 'Science'
            }
        }
        self.wrong_quiz = {
            'previous_questions': [{
                'id': 1,
                'question': 'What is the first month of the year?',
                'answer': 'January',
                'category': 1,
                'difficulty': 1
            }],
            'quiz_category': {
                'id': 10,
                'type': 'Science'
            }
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for
    expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_200_sent_requesting_beyond_valid_page(self):
        """ This test was changed from 404 to 200 because the functionality
        of the GET questions route changed. Instead of aborting with a 404 when
        the list of questions is empty, the user will be presented with an empty
        view but with the correct number of pages.
        """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_delete_question(self):
        new_question = Question(question='Are you happy?',
                                answer='Yes', category=2, difficulty=3)
        new_question.insert()
        res = self.client().delete('/questions/' + str(new_question.id))
        data = json.loads(res.data)

        deleted_question = Question.query.filter(Question.id == new_question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_question.id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(deleted_question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_422_if_question_creation_not_allowed(self):
        res = self.client().post('questions', json=self.bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_sent_requesting_invalid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self. assertEqual(data['message'], 'resource not found')

    def test_search_question_by_term(self):
        res = self.client().post('/searches', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_searching_absent_term(self):
        res = self.client().post('/searches', json=self.absent_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertFalse(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_searching_with_empty_term(self):
        res = self.client().post('/searches', json=self.empty_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_quiz_find_next_question(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quiz_wrong_category(self):
        res = self.client().post('/quizzes', json=self.wrong_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
