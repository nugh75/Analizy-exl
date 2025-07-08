"""
Test per il modulo ai_clients.py
"""
import sys
import os

# Aggiungi la directory utils al path per gli import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    import pytest
    from ai_clients import OpenRouterLLM, create_llm_instance, test_llm_connection
except ImportError:
    print("⚠️  Pytest o moduli utils non disponibili. Esegui test manualmente.")
    
    
def test_openrouter_client():
    """Test client OpenRouter"""
    # Test con parametri mock
    client = OpenRouterLLM(
        model="test-model",
        api_key="test-key", 
        temperature=0.7
    )
    
    assert client.model == "test-model"
    assert client.api_key == "test-key"
    assert client.temperature == 0.7


def test_llm_instance_creation():
    """Test creazione istanza LLM"""
    # Test con configurazioni valide
    config = {
        'provider': 'openrouter',
        'api_key': 'test-key',
        'model': 'test-model'
    }
    
    try:
        llm = create_llm_instance(config)
        assert llm is not None
    except Exception as e:
        # Accettabile se non ci sono credenziali reali
        assert "API" in str(e) or "key" in str(e)


def test_connection_validation():
    """Test validazione connessioni"""
    # Test con configurazione non valida
    result = test_llm_connection({
        'provider': 'openrouter',
        'api_key': 'invalid-key',
        'model': 'test-model'
    })
    
    # Dovrebbe ritornare False per credenziali non valide
    assert result == False


def run_manual_tests():
    """Esegui test manualmente se pytest non disponibile"""
    print("🧪 Esecuzione test manuali per ai_clients...")
    
    try:
        test_openrouter_client()
        print("✅ test_openrouter_client: OK")
    except Exception as e:
        print(f"❌ test_openrouter_client: {e}")
    
    try:
        test_llm_instance_creation()
        print("✅ test_llm_instance_creation: OK")
    except Exception as e:
        print(f"❌ test_llm_instance_creation: {e}")
    
    try:
        test_connection_validation()
        print("✅ test_connection_validation: OK")
    except Exception as e:
        print(f"❌ test_connection_validation: {e}")
    
    print("🔍 Test completati")


if __name__ == "__main__":
    try:
        pytest.main([__file__])
    except:
        run_manual_tests()
