import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_migrate import Migrate

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10
def paginate_pages(request,liss):
    page=request.args.get('page',1,type=int)
    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE
    displayed_questions=[]
    for lis in liss:
        lis_format=lis.format()
        displayed_questions.append(lis_format)
    return  displayed_questions[start:end]
    

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    #database_name = "trivia"
    #database_path = "postgres://{}/{}".format('localhost:5432', database_name)
    data_path='postgresql://caryn:postgres@localhost:5432/trivia'
    setup_db(app,data_path)
    migrate=Migrate(app,db)
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    #CORS(app,resources={r'/*':{"origins":'*'}})
    CORS(app)
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access_Control_Allow_Headers','Content_type')
        response.headers.add('Access_Control_Allow_Methods','GET,POST,DELETE,PATCH,OPTIONS')
        return response
    
    @app.route('/', methods=['POST','GET','PATCH','DELETE','OPTIONS'])
    def index():
        abort(405)
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        try:
            categories=Category.query.all()
            if categories is None:
                abort(404)
            data={}
            for category in categories:
                data[category.id]=category.type
            return jsonify({
                       'success':True,
                     'categories':data,
                     'total_cat':len(data)
                    })
        except:
            abort(404)
        finally:
            db.session.close
            # capability to create new categories
    @app.route('/categories', methods=['POST'])
    def add_new_category():
        try:
            cate=request.get_json()['type']
            cat=Category(type=cate)
            cat.insert()
            cat_lis=[]
            categories=Category.query.all()
            for category in categories:
                cat_elem=category.format()
                cat_lis.append(cat_elem)
            return jsonify({
                'success':True,
                'category_id':cat.id,
                'categories':cat_lis,
                'total_categories':len(cat_lis)
            })
        except:
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def get_questions():
        try:
            questions=Question.query.order_by('id').all()
            if questions is None:
                abort(404)
            displayed_questions=paginate_pages(request,questions)
            if displayed_questions ==[]:
                abort(404)
            current_category=[]
            for question in displayed_questions:
                 current_category.append(question['category'])
            categories=Category.query.all()
            if categories is None:
                abort(404)
            data={}
            for category in categories:
                data[category.id]=category.type
            return jsonify({
                'success':True,
                'questions':displayed_questions,
                'total_questions':len(questions),
                'categories':data,
                'current_category':current_category
            })
        except:
            abort(404)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>' , methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question=Question.query.get(question_id)
            if question is None:
                abort(404)
            question.delet()
            questions=Question.query.all()
            displayed_questions=paginate_pages(request,questions)
            return jsonify({
                'success':True,
                'deleted_id':question_id,
                'questions':displayed_questions,
                'total_questions':len(questions)
            })     
        except:
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def add_new_question():
        try:
            question=request.get_json()['question']
            answer=request.get_json()['answer']
            difficulty=request.get_json()['difficulty']
            category=request.get_json()['category']
            rating=request.get_json()['rating']
            ques=Question(question=question,answer=answer,difficulty=difficulty,category=category,rating=rating)
            ques.insert()
            questions=Question.query.all()
            displayed_questions=paginate_pages(request,questions)
            return jsonify({
                'success':True,
                'question_id':ques.id,
                'questions':displayed_questions,
                'total_questions':len(questions)
            })
        except:
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/search' , methods=['POST'])
    def search_question():
        try:
            search_term=request.get_json()['searchTerm']
            questions=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            displayed_questions=[]
            for question in questions:
                lis_format=question.format()
                displayed_questions.append(lis_format)
            if displayed_questions == []:
                abort(404)
            current_category=[]
            for question in displayed_questions:
                current_category.append(question['category'])
            return jsonify({
                  'success':True,
                  'questions':displayed_questions,
                  'total_questions':len(questions),
                  'current_category':current_category
                          })
        except:
            abort(404)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_question_byid(category_id):
        try:
            questions=Question.query.filter_by(category=category_id).all()
            if questions ==[]:
                abort(404)
            displayed_questions=[]
            for question in questions:
                lis_format=question.format()
                displayed_questions.append(lis_format)
            current_category=[]
            for question in displayed_questions:
                current_category.append(question['category'])
            return jsonify({
                  'success':True,
                  'questions':displayed_questions,
                  'total_questions':len(questions),
                  'current_category':current_category
                          })
        except:
            abort(404)
        finally:
            db.session.close()
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
    @app.route('/quizzes' , methods=['POST'])
    def play():
        try:
            previous_ques=request.get_json()['previous_questions']
            quiz_category=request.get_json()['quiz_category']
            if quiz_category['id']==0 or quiz_category is None:
                questions=Question.query.filter(~Question.id.in_(previous_ques)).all()
            else:
                questions=Question.query.filter(Question.category==quiz_category['id'],~Question.id.in_(previous_ques)).all()
            if questions ==[]:
                question=None
            else:
                ques=random.choice(questions)
                question=ques.format()
            return jsonify({
                'success':True,
                'question':question
            })
        except:
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def Page_Not_Found(error):
        return jsonify({
            "success":False,
            "error":404,
            "message":"Resource Not Found"
        }),404
    @app.errorhandler(400)
    def Bad_reuest(error):
        return jsonify({
            "success":False,
            "error":400,
            "message":"Bad Request"
        }),400
    @app.errorhandler(405)
    def Method_not_allowed(error):
        return jsonify({
            "success":False,
            "error":405,
            "message":"Method_not_allowed"
        }),405
    @app.errorhandler(422)
    def unproceessable(error):
        return jsonify({
            "success":False,
            "error":422,
            "message":"unprocessable_resource"
        }),422
    return app
    
  
  


 


    