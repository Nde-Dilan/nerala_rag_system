from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import logging

from app.services.rag_service import RAGService
from app.utils.validators import RAGCompletionRequest, RAGCompletionResponse

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)
rag_service = RAGService()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Backend',
        'version': '1.0.0'
    })

@api_bp.route('/rag/completion', methods=['POST'])
def rag_completion():
    """Core RAG completion endpoint"""
    try:
        # Validate request
        schema = RAGCompletionRequest()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Invalid request', 'details': err.messages}), 400
        
        # Process RAG completion
        result = rag_service.get_completion(
            query=data['query'],
            language=data['language'],
            top_k=data['top_k']
        )
        
        # Validate and return response
        response_schema = RAGCompletionResponse()
        return jsonify(response_schema.dump(result))
        
    except Exception as e:
        logger.error(f"Error in RAG completion endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process request'
        }), 500

@api_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    from config.settings import Config
    return jsonify({
        'languages': Config.SUPPORTED_LANGUAGES,
        'default_top_k': Config.DEFAULT_TOP_K,
        'max_top_k': Config.MAX_TOP_K
    })

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405