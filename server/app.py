#!/usr/bin/env python3

from flask import make_response, request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        
        data = request.get_json()
        user = User(
            username=data.get('username'), 
            image_url=data.get('image_url'),
            bio=data.get('bio')
            )
        user.password_hash = data.get('password')
        try:
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            
            return make_response(user.to_dict(), 201)
        
        except IntegrityError:
            return {"Error message": "Error signing up. Check credentials."}, 422
class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            return User.query.filter_by(id=session['user_id']).first().to_dict(), 200
        return {"Error message": "401 Unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username==data.get('username')).first()
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200    
        return {"Error": "401 Unauthorized"}, 401
            

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        return {"Error": "401 Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session['user_id']).first()
            if user:
                return [recipe.to_dict() for recipe in user.recipes], 200
            else:
                print("404")
                return {}, 404 
        return {"Error": "401 Unauthorized"}, 401
    
    def post(self):
        if session['user_id']:
            data = request.get_json()
            try:
                recipe = Recipe(
                    title=data.get('title'),
                    instructions=data.get('instructions'),
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            except ValueError as ve:
                return {"Error": str(ve)}, 422
            except IntegrityError:
                return {"Error": "422 Unprocessable Entity"}, 422
        return {"Error": "401 Unauthorized"}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)