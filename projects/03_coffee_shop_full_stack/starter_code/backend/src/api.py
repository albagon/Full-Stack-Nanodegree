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
@TODO   it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks-detail')
def get_drinks_detail():
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

'''
POST /drinks
    it should create a new row in the drinks table
@TODO   it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink or appropriate status
    code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drink():
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

'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
@TODO    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink or appropriate status code
    indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
def update_drink(id):
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

'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
@TODO    it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is
    the id of the deleted record or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(id):
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
