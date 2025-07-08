"""
🤖 AI Clients Module
Gestione client AI per Ollama e OpenRouter
"""

import os
import requests
import json
from langchain_ollama import OllamaLLM
from typing import Union, Dict, List, Any
from dotenv import load_dotenv

# Forza caricamento file .env
load_dotenv(override=True)


class OpenRouterLLM:
    """Wrapper personalizzato per OpenRouter senza dipendere da OpenAI"""
    
    def __init__(self, model: str, api_key: str, temperature: float = 0.7):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]]) -> str:
        """Invoca il modello OpenRouter con i messaggi forniti"""
        
        # Se messages è una stringa, convertila in formato chat
        if isinstance(messages, str):
            formatted_messages = [{"role": "user", "content": messages}]
        else:
            formatted_messages = messages
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8888",
            "X-Title": "Analisi Excel AI",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Errore nella chiamata OpenRouter: {e}")
        except KeyError as e:
            raise Exception(f"Formato risposta OpenRouter non valido: {e}")


def create_llm(provider: str, model: str, temperature: float = 0.7) -> Union[OllamaLLM, OpenRouterLLM]:
    """
    Factory function per creare il client LLM appropriato
    
    Args:
        provider: 'ollama' o 'openrouter'
        model: Nome del modello da utilizzare
        temperature: Temperatura per la generazione
    
    Returns:
        Istanza del client LLM appropriato
    """
    
    if provider.lower() == 'ollama':
        # Usa l'URL personalizzato dal file .env se presente
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        return OllamaLLM(
            model=model,
            temperature=temperature,
            base_url=base_url
        )
    
    elif provider.lower() == 'openrouter':
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY non trovata nelle variabili d'ambiente")
        
        return OpenRouterLLM(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    else:
        raise ValueError(f"Provider {provider} non supportato. Usa 'ollama' o 'openrouter'")


def test_connection(provider: str, model: str = None) -> tuple[bool, str]:
    """
    Testa la connessione con il provider AI
    
    Args:
        provider: 'ollama' o 'openrouter'
        model: Nome del modello da testare (opzionale)
    
    Returns:
        (success: bool, message: str)
    """
    
    try:
        if provider.lower() == 'ollama':
            # Test connessione Ollama con URL personalizzato
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            test_model = model or os.getenv('OLLAMA_MODEL', 'mixtral:8x7b')
            
            # Debug: stampa la configurazione che stiamo usando
            print(f"🔍 Debug Ollama: URL={base_url}, Model={test_model}")
            
            llm = OllamaLLM(model=test_model, temperature=0.1, base_url=base_url)
            response = llm.invoke("Rispondi solo 'OK' se mi ricevi.")
            return True, f"Ollama connesso ({base_url}) con modello {test_model}"
        
        elif provider.lower() == 'openrouter':
            # Test connessione OpenRouter
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                return False, "OPENROUTER_API_KEY non trovata"
            
            if api_key.startswith('sk-or-your-'):
                return False, "API key OpenRouter non configurata (ancora placeholder)"
            
            test_model = model or os.getenv('OPENROUTER_MODEL', 'nvidia/llama-3.1-nemotron-ultra-253b-v1')
            
            # Debug: stampa la configurazione che stiamo usando
            print(f"🔍 Debug OpenRouter: Model={test_model}, API_Key={'***' + api_key[-8:]}")
            
            llm = OpenRouterLLM(model=test_model, api_key=api_key, temperature=0.1)
            response = llm.invoke("Rispondi solo 'OK' se mi ricevi.")
            return True, f"OpenRouter connesso con modello {test_model}"
        
        else:
            return False, f"Provider {provider} non supportato"
    
    except Exception as e:
        return False, f"Errore connessione {provider}: {str(e)}"


def get_available_models(provider: str) -> List[str]:
    """
    Ottiene la lista dei modelli disponibili per il provider
    
    Args:
        provider: 'ollama' o 'openrouter'
    
    Returns:
        Lista dei nomi dei modelli disponibili
    """
    
    if provider.lower() == 'ollama':
        # Lista modelli Ollama comuni (potrebbero variare in base all'installazione)
        return [
            'llama3.2',
            'llama3.2:1b',
            'llama3.2:3b', 
            'mixtral',
            'qwen2.5',
            'phi3',
            'codellama',
            'deepseek-coder'
        ]
    
    elif provider.lower() == 'openrouter':
        # Lista modelli OpenRouter comuni e gratuiti
        return [
            'meta-llama/llama-3.2-3b-instruct:free',
            'meta-llama/llama-3.2-1b-instruct:free',
            'huggingfaceh4/zephyr-7b-beta:free',
            'openchat/openchat-7b:free',
            'gryphe/mythomist-7b:free',
            'undi95/toppy-m-7b:free',
            'openrouter/auto'
        ]
    
    else:
        return []


def estimate_tokens(text: str) -> int:
    """
    Stima approssimativa del numero di token in un testo
    
    Args:
        text: Testo da analizzare
    
    Returns:
        Numero stimato di token
    """
    
    # Stima approssimativa: ~4 caratteri per token
    return len(text) // 4


def validate_model_config(provider: str, model: str) -> tuple[bool, str]:
    """
    Valida la configurazione del modello
    
    Args:
        provider: Provider AI
        model: Nome del modello
    
    Returns:
        (is_valid: bool, message: str)
    """
    
    available_models = get_available_models(provider)
    
    if provider.lower() not in ['ollama', 'openrouter']:
        return False, f"Provider {provider} non supportato"
    
    if model not in available_models:
        return False, f"Modello {model} non disponibile per {provider}"
    
    return True, f"Configurazione {provider}/{model} valida"


def test_all_providers() -> Dict[str, bool]:
    """
    Testa tutti i provider disponibili
    
    Returns:
        Dizionario con lo stato di ogni provider
    """
    
    # Forza ricaricamento variabili d'ambiente
    load_dotenv(override=True)
    
    status = {}
    
    # Test Ollama
    ollama_ok, ollama_msg = test_connection('ollama')
    status['ollama'] = ollama_ok
    
    # Test OpenRouter
    openrouter_ok, openrouter_msg = test_connection('openrouter')
    status['openrouter'] = openrouter_ok
    
    print("🔍 VERIFICA STATO PROVIDER AI")
    print("=" * 50)
    print(f"🏠 Ollama: {'✅' if ollama_ok else '❌'} {ollama_msg}")
    print(f"🌐 OpenRouter: {'✅' if openrouter_ok else '❌'} {openrouter_msg}")
    print("=" * 50)
    
    return status


def create_llm_instance(config: Dict[str, Any]) -> Union[OllamaLLM, OpenRouterLLM]:
    """
    Crea un'istanza LLM basata sulla configurazione
    
    Args:
        config: Configurazione con chiavi 'provider', 'model', 'temperature'
    
    Returns:
        Istanza del client LLM
    """
    
    provider = config.get('provider', 'ollama')
    model = config.get('model')
    temperature = config.get('temperature', 0.7)
    
    # Usa modelli di default se non specificati
    if not model:
        if provider == 'ollama':
            model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        elif provider == 'openrouter':
            model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
    
    return create_llm(provider, model, temperature)
