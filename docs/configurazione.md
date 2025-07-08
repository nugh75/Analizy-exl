# 🔧 Configurazione del Sistema

## Provider AI Supportati

Il sistema supporta due provider principali:

### 🏠 Ollama (Locale)
- **Vantaggi**: Completamente gratuito, privacy totale, nessun limite API
- **Svantaggi**: Richiede installazione locale, maggior consumo risorse
- **Configurazione**: 
  ```bash
  OLLAMA_BASE_URL=http://192.168.129.14:11435
  OLLAMA_MODEL=mixtral:8x7b
  ```

### 🌐 OpenRouter (API)
- **Vantaggi**: Accesso a modelli all'avanguardia, molti gratuiti
- **Svantaggi**: Richiede API key, possibili limiti di utilizzo
- **Configurazione**:
  ```bash
  OPENROUTER_API_KEY=sk-or-your-api-key-here
  OPENROUTER_MODEL=nvidia/llama-3.1-nemotron-ultra-253b-v1
  ```

## Modelli Raccomandati

### Ollama
- **mixtral:8x7b** (26GB) - Molto potente ⭐ CONSIGLIATO
- **deepseek-r1:latest** (4.7GB) - Ragionamento avanzato
- **qwen2.5:7b** (4.7GB) - Equilibrio qualità/velocità
- **phi4:14b** (9.1GB) - Microsoft, buone prestazioni

### OpenRouter
- **nvidia/llama-3.1-nemotron-ultra-253b-v1** - Eccellente qualità ⭐ CONSIGLIATO
- **meta-llama/llama-3.1-8b-instruct:free** - Gratuito e affidabile
- **mistralai/mistral-7b-instruct:free** - Veloce e gratuito
- **google/gemma-2-9b-it:free** - Buona qualità, gratuito

## Configurazione Batch Processing

Il sistema utilizza il batch processing per ottimizzare le performance:

- **BATCH_MODE**: `True` (consigliato per velocizzare)
- **BATCH_SIZE**: `5` (bilanciamento ottimale velocità/qualità)
- **Velocizzazione**: ~5x rispetto al processing singolo
- **Qualità**: Mantenuta alta grazie al prompt ottimizzato

### Vantaggi del Batch Processing
- ⚡ **Velocità**: 5x più veloce del processing singolo
- 💰 **Costi**: Riduzione significativa delle chiamate API
- 🎯 **Qualità**: Mantenuta grazie al contesto condiviso
- 🔧 **Flessibilità**: Dimensione batch configurabile

## Parametri di Analisi

- **SOGLIA_CONFIDENZA**: `0.3` - Soglia minima per accettare un'etichetta
- **ETICHETTE_MULTIPLE**: `True` - Permette etichette multiple per commento
- **SOGLIA_SECONDARIE**: `0.4` - Soglia per etichette aggiuntive
- **MODALITA_ANALISI**: `'balanced'` - Bilanciamento qualità/velocità
- **MAX_ETICHETTE_DINAMICHE**: `20` - Massimo numero di etichette dinamiche

## Template di Prompt

Il sistema include template predefiniti per diversi tipi di analisi:

1. **Feedback Prodotto** - Analisi di feedback su prodotti/servizi
2. **Sentiment Analysis** - Analisi del sentiment dei commenti
3. **Supporto Clienti** - Categorizzazione richieste di supporto
4. **Bug Reports** - Classificazione segnalazioni bug
5. **Feature Requests** - Analisi richieste di funzionalità
6. **Analisi Personalizzata** - Prompt completamente personalizzabile

## File di Configurazione

Il sistema utilizza un file `.env` per la configurazione:

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

## Risoluzione Problemi

### Ollama non raggiungibile
- Verificare che il server Ollama sia in esecuzione
- Controllare l'URL e la porta nel file `.env`
- Testare la connessione: `curl http://192.168.129.14:11435/api/tags`

### OpenRouter API Error
- Verificare che l'API key sia corretta
- Controllare i crediti disponibili
- Verificare che il modello sia supportato

### Performance lente
- Attivare la modalità batch (`BATCH_MODE=True`)
- Aumentare la dimensione batch se necessario
- Scegliere un modello più leggero per test rapidi
