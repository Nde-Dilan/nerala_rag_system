import json
import numpy as np
import google.generativeai as genai
from config.settings import Config
import logging
from huggingface_hub import hf_hub_download
import re

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=Config.GEMINI_MODEL)
        
        # Load pre-computed RAG data
        self._load_rag_data()

        # Common query patterns for word/phrase translation requests
        self.translation_patterns = [
            # How to say/translate patterns
            r"how (?:do|to) (?:you )?say [\"']?(.+?)[\"']?(?:\?|$)",
            r"how (?:do|to) (?:you )?translate [\"']?(.+?)[\"']?(?:\?|$)",
            r"what (?:is|does) [\"']?(.+?)[\"']? (?:mean|in)",
            r"translate [\"']?(.+?)[\"']?(?:\?|$)",
            r"say [\"']?(.+?)[\"']?(?:\?|$)",
            
            # Direct word queries
            r"what is [\"']?(.+?)[\"']?(?:\?|$)",
            r"meaning of [\"']?(.+?)[\"']?(?:\?|$)",
            r"define [\"']?(.+?)[\"']?(?:\?|$)",
            
            # Word in language patterns
            r"[\"']?(.+?)[\"']? in " + r"(fulfulde|ghomala|english|french)",
            r"(fulfulde|ghomala|english|french) (?:word )?for [\"']?(.+?)[\"']?(?:\?|$)",
        ]
        
    def _load_rag_data(self):
        """Load pre-computed embeddings and metadata from JSON"""
        try:
            # Download from Hugging Face
            data_path = hf_hub_download(
                repo_id="nde-dilan/nerala-rag-model", 
                filename="rag_data.json"
            )
            
            with open(data_path, 'r', encoding='utf-8') as f:
                rag_data = json.load(f)
            
            # Load embeddings AND metadata
            self.embeddings = np.array(rag_data['embeddings'])
            self.metadata = rag_data['metadata']
            self.model_info = rag_data['model_info']
            
            # Create language-specific indices for faster lookup
            self.language_indices = {}
            for i, meta in enumerate(self.metadata):
                lang = meta['language']
                if lang not in self.language_indices:
                    self.language_indices[lang] = []
                self.language_indices[lang].append(i)
            
            logger.info(f"RAG data loaded: {len(self.metadata)} documents")
            logger.info(f"Languages: {list(self.language_indices.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load RAG data: {e}")
            self.embeddings = None
            self.metadata = []
            self.model_info = {}
            self.language_indices = {}
    
    def get_completion(self, query: str, language: str, top_k: int = 3) -> dict:
        """Get RAG-enhanced completion with smart query preprocessing"""
        try:
            # Extract the actual word/phrase the user wants to translate
            extracted_terms = self._extract_translation_terms(query)
            
            # Try finding context with extracted terms first
            context = []
            for term in extracted_terms:
                term_context = self._get_relevant_context_semantic(term, language, top_k)
                if not term_context:
                    term_context = self._get_relevant_context_text(term, language, top_k)
                context.extend(term_context)
                
                # If we found good matches, we can stop
                if len(context) >= top_k:
                    break
            
            # Remove duplicates and limit
            context = self._deduplicate_context(context)[:top_k]
            
            # If no specific terms found, try with full query
            if not context:
                context = self._get_relevant_context_semantic(query, language, top_k)
                if not context:
                    context = self._get_relevant_context_text(query, language, top_k)
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(query, language, context, extracted_terms)
            
            # Generate response
            logger.info(f"Extracted terms: {extracted_terms}")
            logger.info(f"Found {len(context)} relevant contexts: {context}")
            response = self.model.generate_content(enhanced_prompt)
            
            return {
                'response': response.text,
                'sources': [item['phrase'] for item in context],
                'language': language,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error in RAG completion: {str(e)}")
            return self._fallback_completion(query, language)
    
    def _extract_translation_terms(self, query: str) -> list:
        """Extract the actual words/phrases user wants to translate"""
        query_lower = query.lower().strip()
        extracted_terms = []
        
        # Try each pattern
        for pattern in self.translation_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with multiple groups, take the relevant one
                    term = match[0] if match[0] else match[1] if len(match) > 1 else ""
                else:
                    term = match
                
                if term and len(term.strip()) > 0:
                    # Clean up the term
                    term = term.strip().strip('"\'').strip('?.,!').strip()
                    if term and len(term) > 1:  # Avoid single characters
                        extracted_terms.append(term)
        
        # If no patterns matched, try to extract quoted words
        quoted_matches = re.findall(r'["\']([^"\']+)["\']', query)
        for match in quoted_matches:
            match = match.strip()
            if match and len(match) > 1:
                extracted_terms.append(match)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in extracted_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)
        
        return unique_terms
    
    def _deduplicate_context(self, context: list) -> list:
        """Remove duplicate context items"""
        seen_phrases = set()
        unique_context = []
        
        for item in context:
            phrase_key = item['phrase'].lower()
            if phrase_key not in seen_phrases:
                seen_phrases.add(phrase_key)
                unique_context.append(item)
        
        return unique_context

    def _get_relevant_context_semantic(self, query: str, language: str, top_k: int) -> list:
        """Use pre-computed embeddings for semantic similarity (EFFICIENT!)"""
        if self.embeddings is None or language not in self.language_indices:
            return []
        
        try:
            # Get language-specific embeddings
            lang_indices = self.language_indices[language]
            lang_embeddings = self.embeddings[lang_indices]
            
            # Simple query embedding using TF-IDF-like approach (no external models!)
            query_embedding = self._create_simple_query_embedding(query, language)
            
            # Calculate cosine similarity
            similarities = self._cosine_similarity(query_embedding, lang_embeddings)
            
            # Get top_k most similar
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            context = []
            for local_idx in top_indices:
                global_idx = lang_indices[local_idx]
                meta = self.metadata[global_idx]
                
                context.append({
                    'phrase': meta['phrase'],
                    'translation': meta['translation'],
                    'category': meta.get('category', 'general'),
                    'score': float(similarities[local_idx])
                })
            
            return [item for item in context if item['score'] > 0.1]  # Filter low scores
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _create_simple_query_embedding(self, query: str, language: str) -> np.ndarray:
        """Create a simple query embedding without external models"""
        # Use pre-computed embeddings to create a pseudo-embedding
        # This is a clever trick to avoid needing sentence-transformers!
        
        query_words = set(query.lower().split())
        
        # Find documents that match query words
        matching_embeddings = []
        lang_indices = self.language_indices.get(language, [])
        
        for idx in lang_indices:
            meta = self.metadata[idx]
            doc_words = set((meta['phrase'] + ' ' + meta['translation']).lower().split())
            
            # If query words overlap with document words, use that embedding
            overlap = len(query_words.intersection(doc_words))
            if overlap > 0:
                weight = overlap / len(query_words)
                matching_embeddings.append((weight, self.embeddings[idx]))
        
        if matching_embeddings:
            # Weighted average of matching embeddings
            total_weight = sum(weight for weight, _ in matching_embeddings)
            if total_weight > 0:
                weighted_embedding = sum(
                    weight * embedding for weight, embedding in matching_embeddings
                ) / total_weight
                return weighted_embedding
        
        # Fallback: average of all language embeddings (rough approximation)
        if lang_indices:
            return np.mean(self.embeddings[lang_indices], axis=0)
        
        # Ultimate fallback: zero vector
        return np.zeros(self.embeddings.shape[1])
    
    def _cosine_similarity(self, query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
        """Efficient cosine similarity calculation"""
        # Normalize vectors
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
        doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-8)
        
        # Calculate similarity
        return np.dot(doc_norms, query_norm)
    
    def _get_relevant_context_text(self, query: str, language: str, top_k: int) -> list:
        """Fallback text-based similarity (your existing method, simplified)"""
        if not self.metadata or language not in self.language_indices:
            return []
        
        query_words = set(query.lower().split())
        lang_indices = self.language_indices[language]
        
        scored_docs = []
        for idx in lang_indices:
            meta = self.metadata[idx]
            
            # Simple word overlap score
            phrase_words = set(meta['phrase'].lower().split())
            translation_words = set(meta['translation'].lower().split())
            
            phrase_score = len(query_words.intersection(phrase_words)) / max(len(query_words), 1)
            translation_score = len(query_words.intersection(translation_words)) / max(len(query_words), 1)
            
            total_score = max(phrase_score, translation_score)  # Take best match
            
            if total_score > 0:
                scored_docs.append((total_score, meta))
        
        # Sort and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                'phrase': meta['phrase'],
                'translation': meta['translation'],
                'category': meta.get('category', 'general'),
                'score': score
            }
            for score, meta in scored_docs[:top_k]
        ]
    
    def _create_enhanced_prompt(self, query: str, language: str, context: list, extracted_terms: list = None) -> str:
        """Create enhanced prompt with extracted terms awareness"""
        language_contexts = {
            'fulfulde': "You are a Fulfulde language expert.",
            'ghomala': "You are a Ghomala language expert.", 
            'english': "You are an English language assistant.",
            'french': "You are a French language assistant."
        }
        
        base_context = language_contexts.get(language, "You are a language assistant.")
        
        if context:
            context_text = "\n".join([
                f"• {item['phrase']} → {item['translation']}"
                for item in context[:5]  # Show more context for better answers
            ])
            
            # Add information about extracted terms
            terms_info = ""
            if extracted_terms:
                terms_info = f"\nThe user is asking about: {', '.join(extracted_terms)}"
            
            prompt = f"""{base_context}
DO NOT ANSWER UNRELATED QUESTIONS OR GIVE UNRELATED INFORMATION.
JUST STAY IN THE LANGUAGE LEARNING DOMAIN! DON'T BE TOO LONG WITH YOUR ANSWERS BUT STILL BE ENJOYABLE TO TALK TO, AND ALWAYS TRY TO PROLONGE COMMUNICATION WITH THE USER!

Relevant {language} translations:
{context_text}{terms_info}

User question: {query}

Based on the translations above, provide a helpful answer. If you found exact translations, present them clearly with pronunciation. If the user is asking "how to say X", focus on the translation of X."""
        else:
            # No context found - but we might have extracted terms
            terms_info = ""
            if extracted_terms:
                terms_info = f" The user seems to be asking about: {', '.join(extracted_terms)}."
            
            prompt = f"""{base_context}
DO NOT ANSWER UNRELATED QUESTIONS OR GIVE UNRELATED INFORMATION.
JUST STAY IN THE LANGUAGE LEARNING DOMAIN! DON'T BE TOO LONG WITH YOUR ANSWERS BUT STILL BE ENJOYABLE TO TALK TO, AND ALWAYS TRY TO PROLONGE COMMUNICATION WITH THE USER!!

User question: {query}{terms_info}

I don't have specific translations for the requested terms in my knowledge base. Provide a helpful response explaining this, and if possible, suggest similar or related terms that might be useful."""
        
        return prompt
    
    def _fallback_completion(self, query: str, language: str) -> dict:
        """Lightweight fallback"""
        try:
            response = self.model.generate_content(f"As a {language} expert: {query}")
            return {
                'response': response.text,
                'sources': [],
                'language': language,
                'query': query
            }
        except:
            return {
                'response': "Sorry, I'm having technical difficulties.",
                'sources': [],
                'language': language,
                'query': query
            }