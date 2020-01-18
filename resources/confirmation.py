import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()

NOT_FOUND = 'Confirmation reference not found.'
EXPIRED = 'Your activation link has expired.'
ALREADY_CONFIRMED = 'Your account has already been confirmed.'
RESEND_SUCCESSFUL = 'A new confirmation mail has been sent to <{}>.'
EMAIL_RESEND_FAILED = 'Oops, we could not resend your email.'


class Confirmation(Resource):
    """Returns the confirmed HTML page"""
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {'message': NOT_FOUND}, 404
        if confirmation.expired:
            return {'message': EXPIRED}, 400
        if confirmation.confirmed:
            return {'message': ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"content-Type": "text/html"}
        return make_response(render_template(
            "confirmation_page.html",
            email=confirmation.user.email),
            200, headers)


class ConfirmationByUser(Resource):
    """Returns a users confirmatin trials."""
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return (
            {
                'current_time': int(time()),
                'confirmations': [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ]
            }
        )

    """Resend confirmation email"""
    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                return {'message': ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user.id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {'message': RESEND_SUCCESSFUL.format(user.email)}
        except MailGunException as error:
            return {'message': str(error)}, 500
        except:
            traceback.print_exc()
            return {'message': EMAIL_RESEND_FAILED}, 500
