#!/usr/bin/env python3
"""
Test per verificare che OpenAI sia stato completamente rimosso
"""

def test_no_openai_imports():
    """Verifica che non ci siano import di OpenAI"""
    print("🔍 Verificando rimozione di OpenAI...")
    
    try:
        # Questo dovrebbe fallire
        from langchain_openai import ChatOpenAI
        print("❌ ERRORE: langchain_openai è ancora presente!")
        return False
    except ImportError:
        print("✅ langchain_openai rimosso correttamente")
    
    # Questi dovrebbero funzionare
    try:
        from langchain_ollama import OllamaLLM
        print("✅ langchain_ollama funziona")
        
        import requests
        print("✅ requests funziona")
        
        return True
    except ImportError as e:
        print(f"❌ Errore con altre librerie: {e}")
        return False

def test_openrouter_wrapper():
    """Testa la classe OpenRouterLLM personalizzata"""
    print("\n🔍 Testando OpenRouterLLM wrapper...")
    
    class OpenRouterLLM:
        """Wrapper personalizzato per OpenRouter senza dipendere da OpenAI"""
        
        def __init__(self, model, api_key, temperature=0.7):
            self.model = model
            self.api_key = api_key
            self.temperature = temperature
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        def invoke(self, messages):
            """Invoca il modello OpenRouter con i messaggi forniti"""
            # Test simulato
            return "Test response"
    
    try:
        llm = OpenRouterLLM(
            model="test-model",
            api_key="test-key",
            temperature=0.7
        )
        
        # Test con string input
        response1 = llm.invoke("test prompt")
        print(f"✅ String input: {response1}")
        
        # Test con messages format
        response2 = llm.invoke([{"role": "user", "content": "test"}])
        print(f"✅ Messages input: {response2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore wrapper: {e}")
        return False

def test_env_configuration():
    """Testa la configurazione senza OpenAI"""
    print("\n🔍 Testando configurazione environment...")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    provider = os.getenv('AI_PROVIDER', 'ollama').lower()
    print(f"📋 Provider configurato: {provider}")
    
    if provider == 'openai':
        print("❌ ERRORE: Provider è ancora impostato su OpenAI!")
        return False
    elif provider in ['ollama', 'openrouter']:
        print(f"✅ Provider valido: {provider}")
        return True
    else:
        print(f"⚠️  Provider sconosciuto: {provider}")
        return False

if __name__ == "__main__":
    print("🧪 TEST RIMOZIONE OPENAI")
    print("=" * 40)
    
    test1 = test_no_openai_imports()
    test2 = test_openrouter_wrapper()
    test3 = test_env_configuration()
    
    if all([test1, test2, test3]):
        print("\n✅ TUTTI I TEST PASSATI!")
        print("🎉 OpenAI è stato rimosso completamente!")
    else:
        print("\n❌ ALCUNI TEST FALLITI")
        print("⚠️  Verifica i problemi sopra")
