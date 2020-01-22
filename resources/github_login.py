from os import environ

from flask import g, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from models.user import UserModel
from oa import github


class GithubLogin(Resource):
    github_callback_url = 'http://localhost:5000/login/github/authorized'

    @classmethod
    def get(cls):
        return github.authorize(callback=cls.github_callback_url)


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        response = github.authorized_response()

        if response is None or response.get('access_token') is None:
            return {
                'error': request.args['error'],
                'error_description': request.args['error_description']
            }

        g.access_token = response['access_token']

        # Makes a GET request to github making use of
        # acess_token in g as auth, therefore, uses the tokengetter decorator in oa.py
        github_user = github.get('user')
        github_username = github_user.data['login']
        github_email = github_user.data['email']

        user = UserModel.find_by_email(github_email)
        if not user:
            user = UserModel(
                username=github_username,
                password='Github',
                email=github_email)

            user.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {'access_token': access_token, 'refresh_token': refresh_token}, 200
