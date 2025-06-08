import os
import logging
from app import create_app

def setup_production_logging():
    """Setup production logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log') if not os.getenv('FLASK_ENV') == 'development' 
            else logging.StreamHandler(),
            logging.StreamHandler()  # Always log to console
        ]
    )

def main():
    """Main application entry point"""
    # Setup logging
    setup_production_logging()
    
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = env == 'development'
    
    if env == 'production':
        # Production settings
        app.logger.info(f"Starting production server on {host}:{port}")
        # Use a production WSGI server like Gunicorn in production
        app.run(host=host, port=port, debug=False, threaded=True)
    else:
        # Development settings
        app.logger.info(f"Starting development server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()