
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message': 'I am working.'
    })
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    data = request.get_json()

    #check if title and recipe are not inside data

    if 'title' and 'recipe' not in data:
        abort(422)
    
    title = data['title']
    recipe_in_json = json.dumps(data['recipe'])

    #create a new drink

    drink = Drink(title=title, recipe=recipe_in_json)

    drink.insert()

    return jsonify({
        'success': True,
        'drinks': drink.long()
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):

    drink = Drink.query.get(id, None)

    #check if drink not found by id

    if drink is None:
        abort(404)
    
    #get data from request

    data = request.get_json()

    #check if title is in data before updating

    if data['title']:
        drink.title = data['title']
    
    #check if recipe is in data before updating

    if data['recipe']:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drink': drink.long()
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>')
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    #check if drink is found

    drink = Drink.query.get(id, None)

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink.id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized",
    }), 401

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response
