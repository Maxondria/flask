from blacklist import BLACKLIST
from db import db
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from libs.image_helper import IMAGE_SET
from ma import ma
from marshmallow import ValidationError
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.user import (TokenRefresh, User, UserLogin, UserLogout,
                            UserRegister)

app = Flask(__name__)

app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')

patch_request_class(app, 10 * 1024 * 1024)  # 10MB max upload size
configure_uploads(app, IMAGE_SET)

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
api.add_resource(Confirmation, '/user_confirmation/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<int:user_id>')
api.add_resource(ImageUpload, '/upload/image')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
