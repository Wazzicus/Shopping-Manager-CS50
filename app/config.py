import os

class Config:
    SECRET_KEY = os.environ.get('jDf#8PzL3rQ!2vXs@5TkW9^mNzH7aEY%UbV0oCMp&RgIqA1dFbJxG$ZKi^lueS')
    SQLALCHEMY_DATABASE_URI = os.environ.get('sqlite:///shopping_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    UPLOAD_FOLDER = 'static/images/avatars'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
