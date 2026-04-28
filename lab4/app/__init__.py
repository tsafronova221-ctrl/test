from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(config_class)
    
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрируем веб-маршруты
    from app import routes
    routes.init_app(app)
    
    # Регистрируем API
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return {
            'datetime': datetime,
            'os': os,
            'len': len,
            'str': str,
            'int': int
        }
    
    return app