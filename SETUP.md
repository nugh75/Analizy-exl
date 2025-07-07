# Analizy-exl - Ambiente di Sviluppo

## 🔧 Setup Virtual Environment

Il virtual environment è già stato creato e configurato per questo progetto.

### Attivazione del Virtual Environment

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Disattivazione
```bash
deactivate
```

### Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### Avvio Jupyter Notebook
```bash
jupyter notebook
# oppure
jupyter lab
```

## 📦 Dipendenze Installate

- **pandas**: Manipolazione dati Excel
- **langchain**: Framework per LLM
- **langchain-community**: Integrazioni provider multipli
- **langchain-ollama**: Integrazione Ollama
- **python-dotenv**: Gestione variabili ambiente
- **python-docx**: Generazione documenti Word
- **ipywidgets**: Widget interattivi Jupyter
- **jupyter**: Ambiente notebook
- **openpyxl**: Lettura/scrittura file Excel
- **xlsxwriter**: Scrittura avanzata Excel
- **requests**: HTTP requests per API
- **httpx**: Client HTTP moderno

## 🔑 Configurazione API Key

Crea un file `.env` nella cartella principale copiando da `.env.example`:

```bash
cp .env.example .env
```

Poi modifica il file `.env` scegliendo il provider AI che preferisci:

### 🏠 **Ollama** (Default - Locale/Gratuito)
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://192.168.129.14:11435
OLLAMA_MODEL=mixtral:8x7b
```

### 🌐 **OpenRouter** (Accesso a modelli multipli, molti gratuiti)
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-la-tua-chiave-openrouter
OPENROUTER_MODEL=nvidia/llama-3.1-nemotron-ultra-253b-v1
```

### 📋 **Modelli Supportati:**

**OpenRouter (Gratuiti):**
- `nvidia/llama-3.1-nemotron-ultra-253b-v1` (Reasoning 253B)
- `deepseek/deepseek-r1-distill-qwen-14b` (Reasoning 14B)
- `arliai/qwq-32b-arliai-rpr-v1` (Creative Writing 32B)
- `mistralai/mistral-small-3` (Fast 24B)
- `reka/reka-flash-3` (General Purpose 21B)
- `featherless/qwerky-72b` (Linear Attention 72B)

**Ollama:**
- `mixtral:8x7b` (Molto potente, raccomandato)
- `deepseek-r1:latest`
- `qwen2.5:7b` / `qwen3:32b`
- `llama4:16x17b`
- `phi4:14b`
- `llama3:latest`

## 🚀 Come Iniziare

1. Attiva il virtual environment
2. Configura la chiave API nel file `.env` (se usi OpenRouter)
3. Avvia Jupyter: `jupyter notebook`
4. Apri `analisi_interattiva.ipynb`
5. Esegui le celle in ordine
