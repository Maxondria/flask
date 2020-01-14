from os import environ

from requests import Response, post
from typing import List


class MailGun:
    FROM_TITLE = 'Stores REST API'
    FROM_EMAIL = 'maxtayebwa@gmail.com'
    MAILGUN_DOMAIN_NAME = environ['MAILGUN_DOMAIN_NAME']
    API_KEY = environ["MAILGUN_API_KEY"]

    @classmethod
    def send_email(cls, emails: List[str], subject: str, text: str, html: str) -> Response:
        MAILGUN_URL = f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN_NAME}/messages"
        return post(
            MAILGUN_URL,
            auth=("api", cls.API_KEY),
            data={"from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                  "to": emails,
                  "subject": subject,
                  "text": text,
                  "html": html})
