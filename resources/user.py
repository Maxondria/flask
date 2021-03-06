import traceback

from blacklist import BLACKLIST
from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, get_raw_jwt,
                                jwt_refresh_token_required, jwt_required, fresh_jwt_required)
from flask_restful import Resource
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.user import UserSchema

BLANK_ERROR = '{} can not be blank'
EMAIL_EXISTS_ALREADY = 'User with email <{}> exists already'
USER_EXISTS_ALREADY = '{} exists already'
USER_CREATED_SUCCESSFULLY = 'An email was sent to <{}>. Please confirm your account'
USER_NOT_FOUND = 'User not found'
USER_DELETED_SUCCESSFULLY = 'User deleted successfully'
INVALID_CREDENTIALS = 'Invalid credentials provided'
USER_LOGGED_OUT = 'Successfully logged out'
NOT_CONFIRMED_ERROR = 'Your email <{}> is not confirmed. Please check your email'
USER_ACCOUNT_CONFIRMED = 'Congrats <{}>, your account has been confirmed'
FAILED_TO_CREATE = 'User couldnot be registered.'
USER_PASSWORD_UPDATED_SUCCESSFULLY = 'User password updated successfully'


user_schema = UserSchema()


class UserRegister(Resource):
    def post(self):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {'message': USER_EXISTS_ALREADY.format(user.username)}, 400

        if UserModel.find_by_email(user.email):
            return {'message': EMAIL_EXISTS_ALREADY.format(user.email)}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {'message': USER_CREATED_SUCCESSFULLY.format(user.email)}, 201
        except MailGunException as error:
            user.delete_from_db()
            return {'message': str(error)}, 500
        except:
            traceback.print_exc(), 500
            user.delete_from_db()
            return {'message': FAILED_TO_CREATE}, 500


class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user_schema.dump(user)

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
        user_data = user_schema.load(request.get_json(), partial=('email',))

        user = UserModel.find_by_username(user_data.username)

        if user and user.password == user_data.password:
            confirmation = user.most_recent_confirmation

            if confirmation and confirmation.confirmed:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {'access_token': access_token, 'refresh_token': refresh_token}, 200
            return {'message': NOT_CONFIRMED_ERROR.format(user.username)}, 400
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


class SetOAuthUserPassword(Resource):
    @classmethod
    @fresh_jwt_required
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)
        verified_email = UserModel.find_by_email(user_data.email)
        verified_username = UserModel.find_by_username(user_data.username)

        if not verified_email or not verified_username:
            return {'message': USER_NOT_FOUND}
        verified_email.password = user_data.password
        verified_email.save_to_db()
        return {'message': USER_PASSWORD_UPDATED_SUCCESSFULLY}, 201
