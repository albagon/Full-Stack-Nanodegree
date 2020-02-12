import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    """
    This is a helper method that retrieves only a set of questions based on
    the page number.

    Arguments:
        request (object) -- the clients request that contains a page number.
        selection (list) -- list of questions we want to paginate.
    Return:
        current_questions (list) -- the set of formatted questions that
        correspond to the page number in the request.
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        """Use the after_request decorator to set Access-Control-Allow."""

        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        """
        This endpoint handles GET requests for all available categories.

        Return:
            success (bool) -- a True value indicating the request was successful.
            categories (list) -- list of all available categories.
            total_categories (int) -- number of categories available.
        """
        categories = Category.query.all()
        formatted_categories = [None] * (len(categories) + 1)

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(categories)
        })

    @app.route('/questions')
    def get_questions():
        """
        This endpoint handles GET requests for questions, including pagination
        (every 10 questions).

        Return:
            success (bool) -- a True value indicating the request was successful.
            questions (list) -- list of questions in this page.
            total_questions (int) -- number of questions in this page.
            current_category (int) -- category id of the 1st question in page.
            categories (list) -- list of all available categories.

        TEST: At this point, when the user starts the application she should see
        questions and categories generated (10 questions per page) and
        pagination at the bottom of the screen for all pages.
        Clicking on the page numbers should update the questions.
        """
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.all()
        formatted_categories = [None] * (len(categories) + 1)

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': current_questions[0]['category'],
            'categories': formatted_categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        This endpoint DELETES one question based on question id.

        Arguments:
            question_id (int) -- the id of the question we want to delete.
        Return:
            success (bool) -- a True value indicating the request was successful.
            deleted (int) -- the id of the question we deleted.
            questions (list) -- list of remaining questions in current page.
            total_questions (int) -- total of questions in Question table.

        TEST: When the user clicks the trash icon next to a question, the
        question will be removed. This removal will persist in the database and
        when the user refreshes the page.
        """
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except Exception:
            abort(404)

    @app.route('/questions', methods=['POST'])
    def create_question():
        """
        This endpoint POSTS a new question, which will require a json object
        containing the question, answer text, category and difficulty score.

        Return:
            success (bool) -- a True value indicating the request was successful.
            created (int) -- the id of the question we created.
            questions (list) -- list of questions in current page.
            total_questions (int) -- total of questions in Question table.

        TEST: When the user submits a question on the "Add" tab, the form will
        clear and the question will appear at the end of the last page of the
        questions list in the "List" tab.
        """
        body = request.get_json()

        question_text = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', 1)
        difficulty = body.get('difficulty', 1)

        try:
            question = Question(question=question_text,
                                answer=answer,
                                category=category,
                                difficulty=difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except Exception:
            abort(422)

    @app.route('/searches', methods=['POST'])
    def search_by_term():
        """
        This endpoint POSTS to get questions based on a search term. It should
        return any questions for whom the search term is a substring of the
        question. It receives a json object containing the search term.

        Return:
            success (bool) -- a True value indicating the request was successful.
            questions (list) -- list of questions with search term.
            total_questions (int) -- total of questions with search term.
            current_category (int) -- category id of the 1st question in list.

        TEST: Search by any phrase. The questions list will update to include
        only question that includes that string within their question.
        Try using the word "title" to start.
        """
        body = request.get_json()
        term = body.get('searchTerm', '')
        current_category = None

        if term == '':
            abort(422)

        questions = Question.query.filter(Question.question.ilike('%'+term+'%')).all()
        formatted_questions = [question.format() for question in questions]

        if len(formatted_questions) > 0:
            current_category = formatted_questions[0]['category']

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': current_category
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_per_category(category_id):
        """
        This endpoint GETS questions based on category.

        Arguments:
            category_id (int) -- the id of the category we want to get.
        Return:
            success (bool) -- a True value indicating the request was successful.
            questions (list) -- list of questions in current category.
            total_questions (int) -- total of questions in current category.
            current_category (int) -- category id we used to get questions.

        TEST: In the "List" tab / main screen, clicking on one of the categories
        in the left column will cause only questions of that category to be
        shown.
        """
        questions = Question.query.filter(Question.category == category_id).all()

        if len(questions) == 0:
            abort(404)

        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def find_next_question():
        """
        This endpoint POSTS to get questions to play the quiz. It should take a
        json object containing category and previous questions as parameters
        and return a random question within the given category,
        if provided, and that is not one of the previous questions.

        Return:
            success (bool) -- a True value indicating the request was successful.
            question (object) -- an unanswered question in current category.

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed. The user is allowed to answer
        and shown whether they were correct or not.
        """
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', 0)
        current_question = None

        if quiz_category['id'] == 0:
            category_questions = Question.query.all()
        else:
            category_questions = Question.query.filter(Question.category == quiz_category['id']).all()

        formatted_cat_questions = [question.format() for question in category_questions]
        random.shuffle(formatted_cat_questions)

        if len(previous_questions) > 0:
            #We need to find a suitable question
            for cat_question in formatted_cat_questions:
                if cat_question['id'] not in previous_questions:
                    #This question hasn't been played
                    current_question = cat_question
                    break
        else:
            #Return the first question from the category we are playing
            current_question = formatted_cat_questions[0]

        return jsonify({
            'success': True,
            'question': current_question
        })

    """
    Error handlers for all expected errors. All of them return a json object
    with the error data just to keep consistent formatting of the responses we
    send to the frontend.

    Arguments:
        error (int) -- the status code responsible for.
    Return:
        success (bool) -- a False value indicating the request was not successful.
        error (int) -- the status code.
        message (string) -- message to the user.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    return app
