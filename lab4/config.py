import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'games.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DATA_DIR = os.path.join(basedir, 'data')
    
    ALLOWED_EXTENSIONS = {'pkl', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024