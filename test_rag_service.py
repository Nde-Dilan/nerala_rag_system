import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import RAGService

def test_lightweight_rag():
    print("🚀 Testing Ultra-Lightweight RAG...")
    
    try:
        rag_service = RAGService()
        print(f"✅ Service initialized")
        print(f"📚 Loaded {len(rag_service.metadata)} documents")
        
        # Test queries
        test_cases = [
            {"query": "How do I say hello?", "language": "fulfulde"},
            {"query": "goodbye", "language": "ghomala"},
            {"query": "numbers", "language": "fulfulde"}
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: '{test['query']}' in {test['language']}")
            
            result = rag_service.get_completion(
                query=test['query'],
                language=test['language'],
                top_k=3
            )
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📚 Sources: {result['sources']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_lightweight_rag()