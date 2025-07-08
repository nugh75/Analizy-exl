# 📊 Analizy-exl - Analisi Interattiva di Commenti Excel con AI

**Sistema modulare per l'analisi qualitativa automatica di commenti Excel con intelligenza artificiale multi-provider**

## 🚀 Quick Start

1. **Configura i provider AI** nel file `.env`
2. **Apri il notebook** `analisi_interattiva.ipynb`
3. **Esegui le celle** in ordine sequenziale
4. **Seleziona** provider AI e file Excel
5. **Analizza** con template predefiniti o prompt personalizzati
6. **Esporta** i risultati in Excel

## 🎯 Caratteristiche Principali

### ⚡ Performance Ottimizzate
- **Batch Processing**: 5x più veloce del processing singolo
- **Multi-Provider**: Ollama (locale) + OpenRouter (cloud)
- **Template Intelligenti**: 5 tipi di analisi predefiniti
- **Interface Guidata**: Configurazione step-by-step

### 🏗️ Architettura Modulare
- **Notebook Pulito**: Solo workflow essenziale 
- **Moduli Utils**: Funzioni riutilizzabili in `/utils/`
- **Documentazione**: Guide complete in `/docs/`
- **Test Suite**: Test automatici in `/tests/`

### 🔧 Facilità d'uso
- **Zero Configurazione**: Rileva automaticamente file e provider
- **Interface Interattiva**: Widget per ogni fase del processo
- **Export Avanzato**: Report multi-sheet con metadati e statistiche
- **Error Handling**: Gestione robusta di errori e fallback

## 📁 Struttura del Progetto

```
Analizy-exl/
├── 📓 analisi_interattiva.ipynb    # Notebook principale (WORKFLOW)
├── 📁 utils/                       # Moduli Python riutilizzabili
│   ├── 🤖 ai_clients.py           # Client AI multi-provider
│   ├── ⚡ batch_processor.py       # Batch processing ottimizzato
│   ├── 📊 data_parsers.py          # Parsing file Excel
│   └── ⚙️ config_manager.py        # Gestione configurazione
├── 📁 docs/                        # Documentazione completa
│   ├── 📖 guida_utente.md          # Guida utente dettagliata
│   └── 🔧 configurazione.md        # Setup e configurazione
├── 📁 tests/                       # Test automatici
│   ├── 🧪 test_integration.py      # Test end-to-end
│   ├── 🔌 test_ai_clients.py       # Test client AI
│   └── ⚡ test_batch_processor.py  # Test batch processing
├── 📄 .env                         # Configurazione provider AI
└── 📋 README.md                    # Questo file
```

## 🤖 Provider AI Supportati

### 🏠 Ollama (Locale/Gratuito)
- **Vantaggi**: Privacy totale, nessun limite, gratuito
- **Modelli raccomandati**: `mixtral:8x7b`, `deepseek-r1:latest`
- **Setup**: Installa Ollama e configura `OLLAMA_BASE_URL`

### 🌐 OpenRouter (Cloud/API)
- **Vantaggi**: Modelli all'avanguardia, molti gratuiti
- **Modelli raccomandati**: `nvidia/llama-3.1-nemotron-ultra-253b-v1`
- **Setup**: Registrati e configura `OPENROUTER_API_KEY`

## ⚙️ Configurazione

Crea un file `.env` nella directory principale:

```bash
# Provider AI (ollama o openrouter)
AI_PROVIDER=ollama
TEMPERATURE=0.7

# Configurazione Ollama
OLLAMA_BASE_URL=http://192.168.129.14:11435
OLLAMA_MODEL=mixtral:8x7b

# Configurazione OpenRouter  
OPENROUTER_API_KEY=sk-or-your-api-key-here
OPENROUTER_MODEL=nvidia/llama-3.1-nemotron-ultra-253b-v1
```

## 📊 Template di Analisi

### 📈 Sentiment Analysis
Analizza sentiment ed emozioni dei commenti
- Sentiment generale (Positivo/Negativo/Neutro)
- Intensità emotiva (Bassa/Media/Alta)
- Emozioni specifiche (Gioia, Rabbia, Tristezza, etc.)

### 💬 Feedback Prodotto
Categorizza feedback su prodotti/servizi
- Aspetti positivi e negativi
- Suggerimenti di miglioramento
- Priorità di intervento

### 🎧 Supporto Clienti
Classifica richieste di supporto
- Tipo di problema
- Livello di urgenza
- Area di competenza

### 🐛 Bug Reports
Analizza segnalazioni di bug
- Severità del problema
- Area coinvolta
- Priorità di risoluzione

### 🎨 Analisi Personalizzata
Template flessibile per esigenze specifiche
- Prompt completamente personalizzabile
- Categorie definite dall'utente

## ⚡ Batch Processing

Il sistema utilizza batch processing per ottimizzare le performance:

- **Modalità Batch**: Raggruppa più commenti in una singola chiamata AI
- **Batch Size Ottimale**: 5 commenti (bilanciamento velocità/qualità)
- **Velocizzazione**: Fino a 5x più veloce del processing singolo
- **Qualità Mantenuta**: Prompt ottimizzato per contesto condiviso

### Vantaggi del Batch Processing
- 🚀 **Velocità**: Riduzione drastica dei tempi di elaborazione
- 💰 **Efficienza**: Meno chiamate API = costi ridotti
- 🎯 **Qualità**: Contesto condiviso migliora la coerenza
- 🔧 **Flessibilità**: Batch size configurabile dall'utente

## 🧪 Test del Sistema

### Test Manuali Rapidi
```bash
# Test di integrazione completo
python tests/test_integration.py

# Test specifici dei moduli
python tests/test_ai_clients.py
python tests/test_batch_processor.py
```

### Test Automatici (se pytest disponibile)
```bash
pip install pytest
pytest tests/ -v
```

## 📖 Documentazione

### Per Utenti
- **📖 [Guida Utente](docs/guida_utente.md)**: Workflow completo e best practices
- **🔧 [Configurazione](docs/configurazione.md)**: Setup dettagliato provider AI

### Per Sviluppatori
- **🏗️ Moduli Utils**: Documentazione in-line nei file `/utils/`
- **🧪 Test Suite**: Esempi di test in `/tests/`
- **📓 Notebook**: Codice commentato per comprensione del workflow

## 🔧 Utilizzo Moduli Python

I moduli in `/utils/` possono essere utilizzati in progetti separati:

```python
# Esempio: Usa batch processor in un altro progetto
from utils.batch_processor import process_comments_batch
from utils.ai_clients import create_llm_instance

# Configura client AI
llm = create_llm_instance({'provider': 'ollama'})

# Processa commenti in batch
results = process_comments_batch(
    comments=['commento 1', 'commento 2'], 
    prompt='Analizza sentiment',
    llm=llm,
    batch_size=5
)
```

## 🎯 Use Cases

### 📚 Ricerca Educativa
- Analisi feedback studenti
- Valutazione programmi formativi
- Sentiment analysis questionari

### 💼 Business Intelligence
- Analisi recensioni prodotti
- Feedback clienti
- Analisi social media

### 🏥 Ricerca Sanitaria
- Feedback pazienti
- Analisi questionari qualità
- Sentiment analysis cure

### 🏛️ Ricerca Sociale
- Analisi interviste qualitative
- Feedback cittadini
- Ricerca opinioni pubbliche

## 🚀 Performance e Scalabilità

### Batch Processing Ottimizzato
- **5-10 commenti/batch**: Ottimale per velocità e qualità
- **Auto-retry**: Gestione automatica errori temporanei
- **Progress Tracking**: Monitoraggio real-time del progresso

### Supporto Dataset Grandi
- **Streaming Processing**: Per file Excel molto grandi
- **Memory Management**: Ottimizzato per uso efficiente della memoria
- **Checkpoint**: Salvataggio intermedio per analisi lunghe

## 🔒 Privacy e Sicurezza

### Ollama (Locale)
- **Privacy Totale**: Dati mai inviati online
- **Controllo Completo**: Server locale sotto il tuo controllo
- **Nessun Limite**: Uso illimitato senza restrizioni

### OpenRouter (Cloud)
- **API Sicure**: Connessioni HTTPS crittografate
- **Dati Temporanei**: Non conservazione dati per training
- **Compliance**: Conforme a standard privacy internazionali

## 🤝 Contributi

Il progetto è strutturato per facilitare contributi:

1. **Fork** del repository
2. **Modifica** i moduli in `/utils/` per nuove funzionalità
3. **Aggiungi test** in `/tests/` per le nuove features
4. **Documenta** le modifiche in `/docs/`
5. **Proponi** una pull request

### Aree di Sviluppo
- 🤖 **Nuovi Provider AI**: Aggiungi supporto per altri LLM
- ⚡ **Ottimizzazioni**: Migliora le performance del batch processing
- 📊 **Visualizzazioni**: Grafici e dashboard per i risultati
- 🔌 **Integrazioni**: Connettori per database e API esterne

## 📞 Supporto

- **🐛 Bug Reports**: Apri una issue su GitHub
- **💡 Feature Requests**: Proponi nuove funzionalità
- **❓ Domande**: Consulta la documentazione in `/docs/`
- **🔧 Problemi Setup**: Segui la guida in `docs/configurazione.md`

---

**📊 Analizy-exl** - Trasforma i tuoi commenti Excel in insights actionable con il potere dell'AI! 🚀