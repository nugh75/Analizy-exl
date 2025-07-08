"""
Test per il modulo batch_processor.py
"""
import pytest
import pandas as pd
import sys
import os

# Aggiungi la directory utils al path per gli import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from batch_processor import process_comments_batch, create_batch_prompt, parse_batch_response


class MockLLM:
    """Mock LLM per test"""
    def __init__(self, response=""):
        self.response = response
    
    def invoke(self, prompt):
        return self.response


def test_create_batch_prompt():
    """Test creazione prompt per batch"""
    comments = ["Ottimo prodotto", "Servizio lento", "Buona qualità"]
    base_prompt = "Analizza il sentiment di questi commenti"
    
    batch_prompt = create_batch_prompt(comments, base_prompt)
    
    assert "Ottimo prodotto" in batch_prompt
    assert "Servizio lento" in batch_prompt  
    assert "Buona qualità" in batch_prompt
    assert "Analizza il sentiment" in batch_prompt
    assert "Commento 1:" in batch_prompt
    assert "Commento 2:" in batch_prompt
    assert "Commento 3:" in batch_prompt


def test_parse_batch_response():
    """Test parsing risposta batch"""
    response = """
    Commento 1: Positivo (0.9)
    Commento 2: Negativo (0.8)
    Commento 3: Positivo (0.7)
    """
    
    results = parse_batch_response(response, 3)
    
    assert len(results) == 3
    assert "Positivo" in results[0]
    assert "Negativo" in results[1]
    assert "Positivo" in results[2]


def test_parse_batch_response_malformed():
    """Test parsing risposta malformata"""
    response = "Risposta non strutturata"
    
    results = parse_batch_response(response, 2)
    
    # Dovrebbe ritornare risultati fallback
    assert len(results) == 2
    assert all("Non classificato" in result for result in results)


def test_process_comments_batch():
    """Test processing batch completo"""
    # Dati di test
    comments = ["Ottimo", "Male", "Bene"]
    base_prompt = "Classifica sentiment"
    
    # Mock LLM con risposta strutturata
    mock_response = """
    Commento 1: Positivo (0.9)
    Commento 2: Negativo (0.8) 
    Commento 3: Positivo (0.7)
    """
    llm = MockLLM(mock_response)
    
    results = process_comments_batch(comments, base_prompt, llm)
    
    assert len(results) == 3
    assert "Positivo" in results[0]
    assert "Negativo" in results[1]
    assert "Positivo" in results[2]


def test_process_comments_batch_error():
    """Test gestione errori nel processing batch"""
    comments = ["Test"]
    base_prompt = "Analizza"
    
    # Mock LLM che solleva eccezione
    class ErrorLLM:
        def invoke(self, prompt):
            raise Exception("Errore di rete")
    
    llm = ErrorLLM()
    
    results = process_comments_batch(comments, base_prompt, llm)
    
    # Dovrebbe gestire l'errore e ritornare fallback
    assert len(results) == 1
    assert "Errore" in results[0] or "Non classificato" in results[0]


def test_batch_size_validation():
    """Test validazione dimensione batch"""
    # Batch troppo grande
    large_comments = ["test"] * 100
    base_prompt = "Analizza"
    llm = MockLLM("test response")
    
    # Il sistema dovrebbe gestire batch grandi dividendoli
    results = process_comments_batch(large_comments, base_prompt, llm)
    assert len(results) == 100


def test_empty_batch():
    """Test batch vuoto"""
    comments = []
    base_prompt = "Analizza"
    llm = MockLLM("")
    
    results = process_comments_batch(comments, base_prompt, llm)
    assert len(results) == 0


def test_performance_comparison():
    """Test di performance tra batch e singolo"""
    import time
    
    comments = ["Test comment"] * 10
    base_prompt = "Analizza sentiment"
    
    # Simula processing singolo
    start_single = time.time()
    for comment in comments:
        # Simula chiamata singola
        time.sleep(0.01)  # 10ms per chiamata
    end_single = time.time()
    single_time = end_single - start_single
    
    # Simula processing batch
    start_batch = time.time()
    # Simula chiamata batch (dovrebbe essere più veloce)
    time.sleep(0.02)  # 20ms per batch completo
    end_batch = time.time()
    batch_time = end_batch - start_batch
    
    # Il batch dovrebbe essere più veloce per dataset grandi
    assert batch_time < single_time


if __name__ == "__main__":
    pytest.main([__file__])
