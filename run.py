import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=app.config['DEBUG']
    )

# pip install Flask Flask-CORS google-generativeai sentence-transformers faiss-cpu pandas numpy python-dotenv marshmallow