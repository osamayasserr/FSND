import os
import sys
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category

# Pagination global variable
QUESTIONS_PER_PAGE = 10


# Application factory
def create_app(test_config=None):

    # Initialize the flask application
    app = Flask(__name__)
    db = setup_db(app)
    cors = CORS(app, resources={r'/*': {'origins': '*'}})

    # Add CORS headers to response
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    # GET /categories
    @app.route('/categories')
    def get_categories():
        try:
            # Query all the categories
            categories = Category.query.all()

            if not categories:
                abort(404)

            # Format the categories
            categories_data = {}
            for category in categories:
                categories_data[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories_data,
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    # GET /questions?page=1
    @app.route('/questions')
    def get_questions():
        try:
            # Get the page no. from query string
            page = int(request.args.get('page', 1))

            # Get paginated questions and format data
            questions = Question.query.paginate(page, QUESTIONS_PER_PAGE)
            questions_data = [question.format()
                              for question in questions.items]

            # Get all categories and format data
            categories = Category.query.all()
            categories_data = {}
            for category in categories:
                categories_data[category.id] = category.type

            return jsonify({
                'success': True,
                'total_questions': questions.total,
                'questions': questions_data,
                'categories': categories_data
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

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

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    return app
