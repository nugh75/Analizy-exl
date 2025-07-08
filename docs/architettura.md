# 🏗️ Architettura del Sistema

## 📋 Panoramica

Il sistema è stato ristrutturato seguendo i principi di **separazione delle responsabilità** e **modularità**, dividendo chiaramente:

- **Notebook**: Solo workflow interattivo e user interface
- **Utils**: Logica di business e funzioni riutilizzabili  
- **Docs**: Documentazione completa e guide
- **Tests**: Suite di test automatici e manuali

## 🎯 Principi di Design

### 1. **Separation of Concerns**
Ogni modulo ha una responsabilità specifica e ben definita:

- `ai_clients.py` → Gestione provider AI
- `batch_processor.py` → Ottimizzazione performance  
- `data_parsers.py` → Manipolazione dati Excel
- `config_manager.py` → Configurazione sistema

### 2. **Reusabilità**
I moduli utils possono essere utilizzati in progetti esterni:

```python
# Esempio: riutilizzo in altro progetto
from utils.batch_processor import process_comments_batch
from utils.ai_clients import create_llm_instance
```

### 3. **Testabilità**
Ogni modulo è testabile in isolamento con mock e stub appropriati.

### 4. **Estensibilità**
Nuovi provider AI o algoritmi di processing possono essere aggiunti facilmente.

## 📁 Struttura Dettagliata

### 📓 Notebook (`analisi_interattiva.ipynb`)
**Responsabilità**: Interface utente e orchestrazione workflow

**Contenuto**:
- Widget interattivi per configurazione
- Progress tracking e feedback utente
- Orchestrazione chiamate ai moduli utils
- Visualizzazione risultati

**Rimosso**:
- Funzioni di business logic
- Test e benchmark
- Documentazione eccessiva
- Celle di debug e sviluppo

### 🔧 Utils (`/utils/`)

#### `ai_clients.py`
**Responsabilità**: Gestione provider AI
```python
# Funzioni principali
- create_llm_instance()    # Factory per client AI
- test_all_providers()     # Verifica provider disponibili
- OpenRouterLLM            # Client OpenRouter personalizzato
```

#### `batch_processor.py`  
**Responsabilità**: Ottimizzazione performance via batch
```python
# Funzioni principali
- process_comments_batch()     # Processing batch ottimizzato
- create_batch_prompt()        # Creazione prompt per batch
- parse_batch_response()       # Parsing risposta batch
- estimate_batch_time()        # Stima tempi processing
```

#### `data_parsers.py`
**Responsabilità**: Manipolazione file Excel
```python
# Funzioni principali  
- load_excel_file()           # Caricamento sicuro Excel
- get_column_info()           # Analisi struttura colonne
- validate_excel_file()       # Validazione formato file
```

#### `config_manager.py`
**Responsabilità**: Gestione configurazione
```python
# Funzioni principali
- load_config()              # Caricamento configurazione
- get_default_config()       # Configurazione default
- validate_config()          # Validazione parametri
```

### 📚 Docs (`/docs/`)

#### `guida_utente.md`
- Workflow completo step-by-step
- Best practices per qualità risultati
- Troubleshooting problemi comuni
- Template di analisi spiegati

#### `configurazione.md`  
- Setup dettagliato provider AI
- Parametri di configurazione
- Ottimizzazione performance
- Risoluzione problemi tecnici

### 🧪 Tests (`/tests/`)

#### `test_integration.py`
- Test end-to-end workflow completo
- Test gestione errori
- Benchmark performance
- Test con dati reali

#### `test_ai_clients.py`
- Test connessioni provider
- Mock delle API esterne
- Test fallback e retry

#### `test_batch_processor.py`
- Test algoritmo batch
- Validazione performance
- Test casi edge

## 🔄 Flusso dei Dati

```
1. 📊 USER INPUT (Notebook)
   ↓ 
2. 🔧 CONFIG LOADING (config_manager)
   ↓
3. 🤖 AI CLIENT SETUP (ai_clients)  
   ↓
4. 📁 DATA LOADING (data_parsers)
   ↓
5. ⚡ BATCH PROCESSING (batch_processor)
   ↓
6. 📊 RESULTS DISPLAY (Notebook)
   ↓
7. 💾 EXPORT (data_parsers)
```

## 🎛️ Interface Layer

Il notebook agisce come **interface layer** che:

1. **Raccoglie input** utente tramite widget
2. **Valida** prerequisiti e configurazione  
3. **Chiama** funzioni utils appropriate
4. **Monitora** progresso e gestisce errori
5. **Visualizza** risultati e permette export

### Widget Principali

- **Provider Selection**: Dropdown + test connessione
- **File Loading**: File picker + anteprima dati  
- **Prompt Configuration**: Template + editor custom
- **Execution Control**: Progress bar + start/stop
- **Results Viewer**: Tabelle + statistiche + export

## 🚀 Performance Architecture

### Batch Processing Pipeline

```
Input Comments → Batching → AI Processing → Parsing → Output
     ↓             ↓           ↓            ↓        ↓
   [1,2,3,4,5] → [[1,2,3],  → [API Call] → [Parse] → [Results]
                  [4,5]]       per batch    Response   Array
```

### Ottimizzazioni Implementate

1. **Batch Grouping**: Riduce chiamate AI da N a N/batch_size
2. **Progress Tracking**: Feedback real-time senza blocking
3. **Error Handling**: Retry automatico + fallback graceful
4. **Memory Management**: Streaming per dataset grandi

## 🔌 Extensibility Points

### Nuovi Provider AI
Aggiungi in `ai_clients.py`:
```python
class NewProviderLLM:
    def __init__(self, config):
        # Setup provider
    
    def invoke(self, prompt):
        # Implementa chiamata API
```

### Nuovi Algoritmi Processing  
Aggiungi in `batch_processor.py`:
```python
def process_comments_advanced(comments, algorithm='sentiment'):
    # Implementa nuovo algoritmo
```

### Nuovi Formati File
Aggiungi in `data_parsers.py`:
```python
def load_csv_file(filepath):
    # Supporto CSV
```

## 🧪 Testing Strategy

### Test Levels

1. **Unit Tests**: Ogni funzione in isolamento
2. **Integration Tests**: Interazione tra moduli
3. **End-to-End Tests**: Workflow completo
4. **Performance Tests**: Benchmark e stress test

### Mock Strategy
- **AI Providers**: Mock delle API esterne
- **File System**: File temporanei per test
- **Network**: Simulazione errori di rete

## 📊 Monitoring e Logging

### Logging Levels
- **INFO**: Workflow normale e milestone
- **DEBUG**: Dettagli tecnici e variabili
- **WARNING**: Problemi non bloccanti  
- **ERROR**: Errori che interrompono il flusso

### Metrics Tracked
- Tempo processing per commento/batch
- Tasso successo/fallimento chiamate AI
- Distribuzione etichette risultanti
- Utilizzo memoria durante processing

## 🔒 Security Considerations

### Data Privacy
- **Ollama**: Dati rimangono locali
- **OpenRouter**: Policy privacy del provider
- **Logging**: Evita log di dati sensibili

### Input Validation
- Sanitizzazione prompt utente
- Validazione formato file Excel
- Controllo dimensioni input

### Error Information
- Messaggi errore non espongono dati interni
- Log dettagliati solo in debug mode
- Gestione sicura delle API key

## 🚀 Future Enhancements

### Architetturali
- **Plugin System**: Loader dinamico per provider
- **Caching Layer**: Cache risultati per prompt simili
- **Queue System**: Processing asincrono per dataset grandi

### Funzionali  
- **Multi-language**: Supporto analisi multilingua
- **Real-time**: Processing real-time di stream dati
- **Collaborative**: Interfaccia multi-utente

### Performance
- **Parallel Processing**: Batch paralleli
- **GPU Acceleration**: Supporto GPU per modelli locali
- **Distributed**: Processing distribuito su cluster
