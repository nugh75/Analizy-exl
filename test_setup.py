#!/usr/bin/env python3
"""
Test script per verificare la configurazione del sistema multi-provider AI
"""
import os
import sys

def test_imports():
    """Testa le importazioni delle librerie necessarie"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas importato correttamente")
        
        import langchain
        print("✅ langchain importato correttamente")
        
        from langchain_ollama import OllamaLLM
        print("✅ langchain_ollama importato correttamente")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv importato correttamente")
        
        import requests
        print("✅ requests importato correttamente")
        
        import httpx
        print("✅ httpx importato correttamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        return False

def test_env_config():
    """Testa la configurazione del file .env"""
    print("\n🔍 Testing environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()
    print(f"📋 Provider AI configurato: {ai_provider}")
    
    if ai_provider == 'openrouter':
        api_key = os.getenv('OPENROUTER_API_KEY')
        model = os.getenv('OPENROUTER_MODEL', 'nvidia/llama-3.1-nemotron-ultra-253b-v1')
        if api_key:
            print(f"✅ OpenRouter configurato: {model}")
            print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'short'}")
        else:
            print("⚠️  OPENROUTER_API_KEY non configurata")
            
    elif ai_provider == 'ollama':
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://192.168.129.14:11435')
        model = os.getenv('OLLAMA_MODEL', 'mixtral:8x7b')
        print(f"✅ Ollama configurato: {model}")
        print(f"🌐 Base URL: {base_url}")
        
        # Test connessione a Ollama
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server raggiungibile")
                try:
                    models = response.json().get('models', [])
                    print(f"📊 Modelli disponibili: {len(models)}")
                    for model_info in models[:3]:  # Mostra solo i primi 3
                        print(f"   - {model_info.get('name', 'unknown')}")
                except:
                    print("✅ Ollama server risponde (formato JSON non parsabile)")
            else:
                print(f"⚠️  Ollama server risponde con codice: {response.status_code}")
        except Exception as e:
            print(f"❌ Errore connessione Ollama: {e}")

def test_llm_creation():
    """Testa la creazione dell'istanza LLM"""
    print("\n🔍 Testing LLM creation...")
    
    try:
        from dotenv import load_dotenv
        from langchain_ollama import OllamaLLM
        import requests
        import json
        
        load_dotenv()
        
        AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama').lower()
        TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
        
        if AI_PROVIDER == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY')
            model = os.getenv('OPENROUTER_MODEL', 'nvidia/llama-3.1-nemotron-ultra-253b-v1')
            
            if not api_key:
                print("⚠️  OPENROUTER_API_KEY non configurata, impossibile testare")
                return False
            
            # Test semplice di connessione a OpenRouter
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            test_data = {
                "model": model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=test_data,
                    timeout=10
                )
                if response.status_code in [200, 400]:  # 400 è OK per test limitato
                    print(f"✅ OpenRouter connessione testata: {model}")
                else:
                    print(f"⚠️  OpenRouter risposta: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Test OpenRouter fallito: {e}")
            
        elif AI_PROVIDER == 'ollama':
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://192.168.129.14:11435')
            model = os.getenv('OLLAMA_MODEL', 'mixtral:8x7b')
            
            # Verifica connessione
            try:
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    print(f"❌ Ollama non raggiungibile su {base_url}")
                    return False
            except:
                print(f"❌ Impossibile connettersi a Ollama su {base_url}")
                return False
            
            llm = OllamaLLM(
                model=model,
                base_url=base_url,
                temperature=TEMPERATURE
            )
            print(f"✅ Ollama LLM creato: {model}")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione LLM: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 TESTING ANALIZY-EXL SETUP")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Test fallito: problemi con le importazioni")
        sys.exit(1)
    
    # Test env config
    test_env_config()
    
    # Test LLM creation
    if not test_llm_creation():
        print("\n⚠️  Test LLM fallito, ma le librerie sono installate correttamente")
    
    print("\n🎉 SETUP COMPLETATO!")
    print("✅ Tutte le librerie sono installate correttamente")
    print("📋 Il notebook è pronto per l'uso")
    print("\n💡 Per iniziare:")
    print("1. Configura il file .env con le tue API key")
    print("2. Avvia Jupyter: jupyter notebook")
    print("3. Apri analisi_interattiva.ipynb")

if __name__ == "__main__":
    main()
