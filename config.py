from os import environ, path


SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{environ["MYSQL_USER"]}:{environ["MYSQL_PASSWORD"]}@{environ["MYSQL_HOST"]}/{environ["MYSQL_DB"]}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = environ['JWT_SECRET']
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
UPLOADED_IMAGES_DEST = path.join('static', 'images')
SECRET_KEY = environ['APP_SECRET_KEY']
