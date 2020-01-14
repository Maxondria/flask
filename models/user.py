from os import environ

from db import db
from flask import request, url_for
from requests import Response, post
from libs.mailgun import MailGun


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

    def send_confirmation_email(self) -> Response:
        # http://localhost:5000 + /confirm/1
        link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        subject = "Registration Confirmation"
        text = "Please click the link to confirm regsitration"
        html = f'<p><a href="{link}"/>{link}</a></p>'
        emails = [self.email]

        return MailGun.send_email(emails=emails, subject=subject, text=text, html=html)

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
