from marshmallow import Schema, fields, validate, ValidationError
from config.settings import Config

class RAGCompletionRequest(Schema):
    query = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    language = fields.Str(
        required=True, 
        validate=validate.OneOf(Config.SUPPORTED_LANGUAGES)
    )
    top_k = fields.Int(
        missing=Config.DEFAULT_TOP_K,
        validate=validate.Range(min=1, max=Config.MAX_TOP_K)
    )

class RAGCompletionResponse(Schema):
    response = fields.Str(required=True)
    sources = fields.List(fields.Str(), missing=[])
    language = fields.Str(required=True)
    query = fields.Str(required=True)