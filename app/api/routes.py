# from flask import Blueprint, request, jsonify
# from marshmallow import ValidationError
# import logging

# from app.services.rag_service import RAGService
# from app.utils.validators import RAGCompletionRequest, RAGCompletionResponse

# logger = logging.getLogger(__name__)

# api_bp = Blueprint('api', __name__)
# rag_service = RAGService()

# @api_bp.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'status': 'healthy',
#         'service': 'RAG Backend',
#         'version': '1.0.0'
#     })

# @api_bp.route('/rag/completion', methods=['POST'])
# def rag_completion():
#     """Core RAG completion endpoint"""
#     try:
#         # Validate request
#         schema = RAGCompletionRequest()
#         try:
#             data = schema.load(request.json)
#         except ValidationError as err:
#             return jsonify({'error': 'Invalid request', 'details': err.messages}), 400
        
#         # Process RAG completion
#         result = rag_service.get_completion(
#             query=data['query'],
#             language=data['language'],
#             top_k=data['top_k']
#         )
        
#         # Validate and return response
#         response_schema = RAGCompletionResponse()
#         return jsonify(response_schema.dump(result))
        
#     except Exception as e:
#         logger.error(f"Error in RAG completion endpoint: {str(e)}")
#         return jsonify({
#             'error': 'Internal server error',
#             'message': 'Failed to process request'
#         }), 500

# @api_bp.route('/languages', methods=['GET'])
# def get_supported_languages():
#     """Get list of supported languages"""
#     from config.settings import Config
#     return jsonify({
#         'languages': Config.SUPPORTED_LANGUAGES,
#         'default_top_k': Config.DEFAULT_TOP_K,
#         'max_top_k': Config.MAX_TOP_K
#     })

# @api_bp.errorhandler(404)
# def not_found(error):
#     return jsonify({'error': 'Endpoint not found'}), 404

# @api_bp.errorhandler(405)
# def method_not_allowed(error):
#     return jsonify({'error': 'Method not allowed'}), 405







from flask import Blueprint, request, jsonify
import logging

from app.services.rag_service import RAGService

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
        # Simple validation without marshmallow
        data = request.json
        
        if not data or 'query' not in data or 'language' not in data:
            return jsonify({'error': 'Missing required fields: query, language'}), 400
        
        query = data['query']
        language = data['language']
        top_k = data.get('top_k', 3)
        
        # Basic validation
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        if language not in ['fulfulde', 'ghomala', 'english', 'french']:
            return jsonify({'error': 'Unsupported language'}), 400
        
        if not isinstance(top_k, int) or top_k < 1 or top_k > 10:
            return jsonify({'error': 'top_k must be between 1 and 10'}), 400
        
        # Process RAG completion
        result = rag_service.get_completion(
            query=query,
            language=language,
            top_k=top_k
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in RAG completion endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process request'
        }), 500

@api_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'languages': ['fulfulde', 'ghomala', 'english', 'french'],
        'default_top_k': 3,
        'max_top_k': 10
    })

@api_bp.route('/debug/rag-components', methods=['GET'])
def debug_rag_components():
    """Debug endpoint to check RAG components status"""
    try:
        has_metadata = hasattr(rag_service, 'metadata') and len(rag_service.metadata) > 0
        
        return jsonify({
            'rag_components_loaded': has_metadata,
            'has_metadata': has_metadata,
            'metadata_count': len(rag_service.metadata) if has_metadata else 0,
            'supported_languages': list(set([item.get('language', 'unknown') for item in rag_service.metadata])) if has_metadata else []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405