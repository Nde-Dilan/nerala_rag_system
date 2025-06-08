from flask import Flask, jsonify, request
from flask_cors import CORS
from config.settings import config
import logging
import os
from datetime import datetime

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Validate configuration
    try:
        config[config_name].validate_config()
    except ValueError as e:
        app.logger.error(f"Configuration error: {e}")
        raise
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register middleware
    register_middleware(app)
    
    app.logger.info(f"Application created with config: {config_name}")
    return app

def setup_logging(app):
    """Configure logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/nerala_rag.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Nerala RAG Backend startup')

def register_blueprints(app):
    """Register application blueprints"""
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix=f'/api/{app.config["API_VERSION"]}')

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({'error': 'Request too large', 'message': 'Request size exceeds limit'}), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate limit exceeded', 'message': 'Too many requests'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

def register_middleware(app):
    """Register middleware"""
    
    @app.before_request
    def log_request_info():
        if not app.debug:
            app.logger.info(f'{request.method} {request.url} - {request.remote_addr}')
    
    @app.after_request
    def after_request(response):
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if not app.debug:
            app.logger.info(f'{request.method} {request.url} - {response.status_code}')
        
        return response
    
    @app.route('/health')
    def health_check():
        """Root health check"""
        return jsonify({
            'status': 'healthy',
            'service': 'Nerala RAG Backend',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })