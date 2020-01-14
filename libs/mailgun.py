from os import environ

from requests import Response, post
from typing import List


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


MAILGUN_DOMAIN_NAME_ERROR = 'Failed to load Mailgun domain name'
MAILGUN_API_KEY_ERROR = 'Failed to load Mailgun API KEY'


class MailGun:
    FROM_TITLE = 'Stores REST API'
    FROM_EMAIL = 'maxtayebwa@gmail.com'
    MAILGUN_DOMAIN_NAME = environ['MAILGUN_DOMAIN_NAME']
    API_KEY = environ["MAILGUN_API_KEY"]

    @classmethod
    def send_email(cls, emails: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_DOMAIN_NAME is None:
            raise MailGunException(MAILGUN_DOMAIN_NAME_ERROR)

        if cls.API_KEY is None:
            raise MailGunException(MAILGUN_API_KEY_ERROR)

        MAILGUN_URL = f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN_NAME}/messages"

        response = post(
            MAILGUN_URL,
            auth=("api", cls.API_KEY),
            data={"from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                  "to": emails,
                  "subject": subject,
                  "text": text,
                  "html": html})

        if response.status_code != 200:
            raise MailGunException('Sending Email Failed')
        return response
