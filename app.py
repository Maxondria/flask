from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from os import environ
from db import db
from ma import ma
from blacklist import BLACKLIST

from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList

from marshmallow import ValidationError

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = environ['JWT_SECRET']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@mysql/advanced_flask_restful'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

db.init_app(app)
ma.init_app(app)


api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(error):
    return jsonify(error.messages), 400


jwt = JWTManager(app)


# add more data to the token other than simply identity
@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blacklist_loader
def check_if_token_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

# detect expiration of tokens
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'description': 'No signature was found in request',
        'error': 'user_unauthorized'
    }), 401


@jwt.needs_fresh_token_loader
def fresh_token_callback():
    return jsonify({
        'description': 'Please login again',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'Please contact admin',
        'error': 'token_revoked'
    }), 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
