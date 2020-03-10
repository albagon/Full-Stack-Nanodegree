import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

''' This function gets the permission in jwt authorization header
'''
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        abort(401)
    elif header_parts[0].lower() != 'bearer':
        abort(401)
    return header_parts[1]

def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        jwt = get_token_auth_header()
        return f(jwt, *args, **kwargs)
    return wrapper


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# Insert a couple of records so we can test our endpoints
chai = Drink(title="Chai Latte", recipe=str([{"color": "#f1d6ab", "name":"milk", "parts":2}, {"color": "#a5642a", "name":"chai", "parts":1}]))
chai.insert()
cortado = Drink(title="Cortado", recipe=str([{"color": "#f1d6ab", "name":"milk", "parts":1}, {"color": "#824f22", "name":"coffee", "parts":2}]))
cortado.insert()

## ROUTES
'''
GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_short = []
        if len(drinks) != 0:
            for drink in drinks:
                # We need to replace all single quotes with double quotes in
                # order to make the recipe valid as a JSON string.
                drink.recipe = drink.recipe.replace("\'", "\"")
                drinks_short.append(drink.short())

        return jsonify({
                "success": True,
                "drinks": drinks_short
            })

    except Exception:
        abort(404)

'''
GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks-detail')
@requires_auth
def get_drinks_detail(jwt):
    if jwt == 'get:drinks-detail':
        try:
            drinks = Drink.query.all()
            drinks_detail = []
            if len(drinks) != 0:
                for drink in drinks:
                    # We need to replace all single quotes with double quotes in
                    # order to make the recipe valid as a JSON string.
                    drink.recipe = drink.recipe.replace("\'", "\"")
                    drinks_detail.append(drink.long())

            return jsonify({
                    "success": True,
                    "drinks": drinks_detail
                })

        except Exception:
            abort(404)
    else:
        abort(401)

'''
POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink or appropriate status
    code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth
def create_drink(jwt):
    if jwt == 'post:drinks':
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        try:
            drink = Drink(title=title, recipe=str(recipe))
            drink.insert()
            # We need to replace all single quotes with double quotes in
            # order to make the recipe valid as a JSON string.
            drink.recipe = drink.recipe.replace("\'", "\"")
            drink_list = []
            drink_list.append(drink.long())

            return jsonify({
                    "success": True,
                    "drinks": drink_list
                })

        except Exception:
            abort(422)
    else:
        abort(401)

'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink or appropriate status code
    indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth
def update_drink(jwt, id):
    if jwt == 'patch:drinks':
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink == None:
                abort(404)
            else:
                drink.title = title
                drink.recipe = str(recipe)
                drink.update()
                # We need to replace all single quotes with double quotes in
                # order to make the recipe valid as a JSON string.
                drink.recipe = drink.recipe.replace("\'", "\"")
                drink_list = []
                drink_list.append(drink.long())

                return jsonify({
                        "success": True,
                        "drinks": drink_list
                    })

        except Exception:
            abort(404)
    else:
        abort(401)

'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is
    the id of the deleted record or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth
def delete_drink(jwt, id):
    if jwt == 'delete:drinks':
        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink == None:
                abort(404)
            else:
                drink.delete()

                return jsonify({
                        "success": True,
                        "delete": id
                    })

        except Exception:
            abort(404)
    else:
        abort(401)

## Error Handling
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401
