from flask_restful import Resource, reqparse
from models.user import UserModel
from blacklist import BLACKLIST
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                get_jwt_identity,
                                get_raw_jwt,
                                jwt_refresh_token_required)

BLANK_ERROR = '{} can not be blank'
USER_EXISTS_ALREADY = '{} exists already'
USER_CREATED_SUCCESSFULLY = 'User {} created successfully'
USER_NOT_FOUND = 'User not found'
USER_DELETED_SUCCESSFULLY = 'User deleted successfully'
INVALID_CREDENTIALS = 'Invalid credentials provided'
USER_LOGGED_OUT = 'Successfully logged out'

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help=BLANK_ERROR.format('username')
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help=BLANK_ERROR.format('password')
                          )


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': USER_EXISTS_ALREADY.format(data['username'])}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': USER_CREATED_SUCCESSFULLY.format(data['username'])}, 201


class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user.json()

    @classmethod
    @jwt_required
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {'message': USER_DELETED_SUCCESSFULLY}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])

        if user and user.password == data['password']:
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        return {'message': INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        # JWT id, A unique identfier for the token
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': USER_LOGGED_OUT}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
