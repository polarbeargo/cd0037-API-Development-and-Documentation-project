import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        # categories data in dict format which will contain category id as key and type as value 
        formatted_categories = {category.id: category.type for category in categories}

        if categories is None:
            abort(404)
        
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            # Use the paginate method already provide in the flask-sqlalchemy
            current_questions = Question.query.order_by(Question.id).paginate(page=1, per_page=QUESTIONS_PER_PAGE).items

            current_questions = [question.format() for question in current_questions]
            categories = Category.query.all()
            # categories data in dict format which will contain category id as key and type as value 
            formatted_categories = {category.id: category.type for category in categories}

            if len(current_questions) == 0:
                abort(404)
       

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'categories': formatted_categories,
                'current_category': None
            })
        
        except Exception as e:
            print(e)
            abort(422)


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
        
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if body is None:
            abort(400)

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        if question is None or answer is None or difficulty is None or category is None:
            abort(422)
        
        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })
        
        except Exception as e:
            print(e)
            abort(422)
            
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        if body is None:
            abort(400)
        
        search_term = body.get('searchTerm', None)

        if search_term is None:
            abort(422)
        
        try:
            selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            # Use the paginate method already provide in the flask-sqlalchemy
            current_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).paginate(page=1, per_page=QUESTIONS_PER_PAGE).items
            current_questions = [question.format() for question in current_questions]

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        
        except Exception as e:
            print(e)
            abort(422)
        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            category = Category.query.filter(Category.id == category_id).one_or_none()

            if category is None:
                abort(404)
        
            selection = Question.query.filter(Question.category == category_id).all()
            # Use the paginate method already provide in the flask-sqlalchemy
            current_questions = Question.query.filter(Question.category == category_id).paginate(page=1, per_page=QUESTIONS_PER_PAGE).items
            current_questions = [question.format() for question in current_questions]
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': category.type
            })
        
        except Exception as e:
            print(e)
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            if body is None:
                abort(400)
        
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            if previous_questions is None or quiz_category is None:
                abort(422)
        
            if quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                # Use notin_() method of SQLAlchemy to check if the question id is not in the previous questions
                questions = Question.query.filter(Question.category == quiz_category['id'] and Question.id.notin_(previous_questions)).all()
        
            if len(questions) == 0:
                abort(404)

            question = random.choice(questions)
          
            return jsonify({
                'success': True,
                'question': question.format()
            })
        
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422
        
    return app

