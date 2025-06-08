from flask import Flask
from flask_cors import CORS
from config.settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for Flutter app
    CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix=f'/api/{Config.API_VERSION}')
    
    return app