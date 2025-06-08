import google.generativeai as genai
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=Config.GEMINI_MODEL)
        
    def get_completion(self, query: str, language: str, top_k: int = 3) -> dict:
        """
        Get RAG-enhanced completion for the given query.
        For now, this is a simplified version that will be enhanced with vector search.
        """
        try:
            # TODO: Implement vector search and context retrieval
            # For now, we'll create a simple language-aware prompt
            
            enhanced_prompt = self._create_enhanced_prompt(query, language)
            
            # Generate response using Gemini
            response = self.model.generate_content(enhanced_prompt)
            
            return {
                'response': response.text,
                'sources': [],  # TODO: Add actual sources from vector search
                'language': language,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error in RAG completion: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")
    
    def _create_enhanced_prompt(self, query: str, language: str) -> str:
        """Create a language-specific enhanced prompt"""
        
        language_context = {
            'fulfulde': """You are an expert in Fulfulde (Fula) language and culture. 
            Fulfulde is spoken by the Fula people across West and Central Africa.
            Provide accurate translations, cultural context, and pronunciation guidance when relevant.""",
            
            'ghomala': """You are an expert in Ghomala language and Bamileke culture.
            Ghomala is spoken by the Bamileke people in the Western Region of Cameroon.
            Provide accurate translations, cultural context, and pronunciation guidance when relevant.""",
            
            'english': """You are an English language learning assistant.
            Provide clear explanations, grammar rules, and usage examples.""",
            
            'french': """You are a French language learning assistant.
            Provide accurate translations, grammar explanations, and cultural context."""
        }
        
        context = language_context.get(language, "You are a helpful language learning assistant.")
        
        enhanced_prompt = f"""{context}

User query: {query}

Please provide a helpful, accurate, and culturally appropriate response. 
If providing translations, include pronunciation guidance when possible.
Keep your response conversational and educational."""

        return enhanced_prompt