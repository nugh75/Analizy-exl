# 🧪 Test Suite per Analisi Commenti Excel

Questo modulo contiene test automatici per verificare il corretto funzionamento del sistema di analisi.

## Esecuzione dei Test

```bash
# Installa le dipendenze per i test
pip install pytest pytest-cov

# Esegui tutti i test
python -m pytest tests/ -v

# Esegui con coverage
python -m pytest tests/ --cov=utils --cov-report=html
```

## Test Disponibili

### test_batch_processor.py
- Test del batch processing
- Validazione formato output
- Test performance
- Gestione errori

### test_ai_clients.py  
- Test connessioni AI providers
- Validazione risposte
- Test timeout e retry
- Fallback tra providers

### test_data_parsers.py
- Test parsing file Excel
- Validazione colonne
- Gestione file corrotti
- Test formati diversi

### test_config_manager.py
- Test caricamento configurazione
- Validazione parametri
- Test file .env
- Gestione errori config

### test_integration.py
- Test end-to-end completi
- Workflow integrati
- Test su dati reali
- Benchmark performance
