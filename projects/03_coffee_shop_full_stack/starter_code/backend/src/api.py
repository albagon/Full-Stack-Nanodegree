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
tea = Drink(title="Mint Tea", recipe=str([{"color": "#cae2ca", "name":"mint", "parts":1}]))
tea.insert()

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
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    if payload:
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
@requires_auth('post:drinks')
def create_drink(payload):
    if payload:
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
@requires_auth('patch:drinks')
def update_drink(payload, id):
    if payload:
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
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    if payload:
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
    error handler for 401
    error handler should conform to general task
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401

'''
    error handler for 403
    error handler should conform to general task
'''
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "forbidden"
                    }), 403

'''
    error handler for 404
    error handler should conform to general task
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

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
    error handler for AuthError
    error handler should conform to general task
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
