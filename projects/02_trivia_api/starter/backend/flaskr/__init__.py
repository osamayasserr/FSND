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
            abort(422)

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

            if not questions_data or not categories:
                abort(404)

            return jsonify({
                'success': True,
                'total_questions': questions.total,
                'questions': questions_data,
                'categories': categories_data,
                'current_category': None
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()

    # DELETE /questions/id
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # Get the question by id
            question = Question.query.get(id)

            if not question:
                abort(404)

            # Delete question
            db.session.delete(question)
            db.session.commit()

            return jsonify({
                'success': True,
                'id': question.id
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()

    # POST /questions
    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            # Get the data submitted
            data = request.get_json()
            question = data.get('question')
            answer = data.get('answer')
            difficulty = int(data.get('difficulty'))
            category = data.get('category')

            if not (data and question and answer and difficulty and category):
                abort(400)

            # Create a new question and add it
            new_question = Question(question, answer, difficulty, category)
            db.session.add(new_question)
            db.session.commit()

            return jsonify({
                'success': True,
                'id': new_question.id
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()

    # POST /questions/search
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            # Get the search term
            data = request.get_json()
            search_term = data.get('searchTerm')

            # if not search_term:
            #     abort(400)

            # Query the database based on search
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            questions = [question.format() for question in questions]

            # if not questions:
            #     abort(404)

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': None
            }), 200

        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()

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
