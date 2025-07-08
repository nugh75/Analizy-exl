# 📊 Guida Utente - Analisi Interattiva di Commenti Excel

## 🎯 Panoramica

Questo sistema permette di analizzare e etichettare automaticamente commenti da file Excel utilizzando modelli di intelligenza artificiale. L'interfaccia interattiva semplifica il processo di analisi qualitativa dei dati.

## 🚀 Quick Start

### 1. Avvio del Sistema
1. Assicurati che il file `.env` sia configurato correttamente
2. Apri il notebook `analisi_interattiva.ipynb`
3. Esegui tutte le celle in ordine sequenziale

### 2. Selezione Provider AI
- **Ollama**: Ideale per uso locale e privacy
- **OpenRouter**: Accesso a modelli cloud avanzati
- Il sistema mostra automaticamente i provider disponibili

### 3. Caricamento File Excel
- Seleziona il file dalla lista o specifica un percorso personalizzato
- Il sistema rileva automaticamente le colonne disponibili
- Scegli la colonna contenente i commenti da analizzare

### 4. Configurazione Analisi
- Scegli un template di prompt predefinito o crea uno personalizzato
- Configura i parametri avanzati se necessario
- Attiva la modalità batch per analisi più veloce

### 5. Esecuzione e Risultati
- Avvia l'analisi e monitora il progresso
- Visualizza i risultati nell'interfaccia avanzata
- Esporta i risultati in formato Excel

## 📋 Workflow Dettagliato

### Fase 1: Preparazione
1. **Verifica Configurazione**: Il sistema controlla automaticamente i provider AI
2. **Selezione Provider**: Scegli tra Ollama e OpenRouter
3. **Test Connessione**: Verifica che il provider selezionato funzioni

### Fase 2: Caricamento Dati
1. **Selezione File**: Carica il file Excel da analizzare
2. **Anteprima Dati**: Visualizza un campione del file
3. **Selezione Colonna**: Identifica la colonna con i commenti

### Fase 3: Configurazione Prompt
1. **Template Predefiniti**: Scegli tra i template disponibili
2. **Personalizzazione**: Modifica il prompt secondo le tue esigenze
3. **Anteprima**: Verifica come apparirà il prompt finale

### Fase 4: Configurazione Avanzata
1. **Parametri Qualità**: Soglie di confidenza e modalità analisi
2. **Batch Processing**: Attiva per velocizzare l'analisi
3. **Etichette Multiple**: Permetti più etichette per commento

### Fase 5: Analisi
1. **Avvio**: Inizia il processo di analisi automatica
2. **Monitoraggio**: Segui il progresso in tempo reale
3. **Gestione Errori**: Il sistema gestisce automaticamente i problemi

### Fase 6: Risultati
1. **Visualizzazione**: Esamina i risultati nell'interfaccia
2. **Analisi Qualità**: Metriche di confidenza e distribuzione
3. **Esportazione**: Salva i risultati in Excel

## 🎛️ Interfacce Disponibili

### Interface Selezione Provider
- Dropdown per scegliere il provider AI
- Informazioni sui modelli disponibili
- Test di connessione automatico

### Interface Caricamento File
- Lista file Excel nella directory corrente
- Campo per percorso personalizzato
- Anteprima automatica del contenuto

### Interface Configurazione Prompt
- Template predefiniti per diversi tipi di analisi
- Editor per prompt personalizzati
- Anteprima del prompt finale

### Interface Configurazione Avanzata
- Slider per soglie di confidenza
- Checkbox per etichette multiple
- Controlli batch processing

### Interface Esecuzione
- Barra di progresso dell'analisi
- Informazioni sui tempi stimati
- Log degli errori e successi

### Interface Risultati Avanzata
- Tabella risultati dettagliata
- Metriche di qualità dell'analisi
- Controlli per esportazione

## 📊 Template di Prompt

### Feedback Prodotto
Analizza feedback su prodotti e servizi, identificando:
- Aspetti positivi e negativi
- Suggerimenti di miglioramento
- Priorità di intervento

### Sentiment Analysis
Classifica i commenti per sentiment:
- Positivo, Negativo, Neutro
- Intensità emotiva
- Temi ricorrenti

### Supporto Clienti
Categorizza richieste di supporto:
- Tipo di problema
- Urgenza
- Area di competenza

### Bug Reports
Analizza segnalazioni di bug:
- Severità del problema
- Area coinvolta
- Riproducibilità

### Feature Requests
Classifica richieste di funzionalità:
- Priorità
- Complessità implementativa
- Impatto utenti

## ⚡ Ottimizzazione Performance

### Modalità Batch
- **Attivazione**: Raccomandato per file con molti commenti
- **Dimensione**: 5 commenti per batch (ottimale)
- **Velocizzazione**: Fino a 5x più veloce
- **Qualità**: Mantenuta alta grazie al contesto condiviso

### Scelta del Modello
- **Modelli veloci**: Per test e analisi rapide
- **Modelli potenti**: Per analisi di qualità massima
- **Bilanciamento**: Considerare velocità vs. qualità

### Gestione Errori
- Retry automatico per errori temporanei
- Fallback a modelli alternativi
- Log dettagliato per debug

## 🔧 Risoluzione Problemi

### Problemi Comuni

#### File Excel non caricato
- Verifica che il file sia in formato .xlsx
- Controlla i permessi di lettura
- Assicurati che il file non sia corrotto

#### Provider AI non disponibile
- Verifica la configurazione nel file `.env`
- Testa la connessione di rete
- Controlla che il servizio sia in esecuzione

#### Analisi lenta
- Attiva la modalità batch
- Riduci la dimensione del dataset per test
- Usa un modello più veloce

#### Risultati di bassa qualità
- Migliora il prompt con esempi specifici
- Aumenta la soglia di confidenza
- Usa un modello più potente

### Log e Debug
- I log sono salvati in `operazioni_log.log`
- Attiva il debug per informazioni dettagliate
- Monitora l'output delle celle per errori

## 📈 Best Practices

### Preparazione Dati
1. **Pulizia**: Rimuovi commenti vuoti o non significativi
2. **Formato**: Assicurati che i commenti siano in una singola colonna
3. **Campione**: Testa su un piccolo campione prima dell'analisi completa

### Configurazione Prompt
1. **Specificità**: Sii specifico sulle categorie desiderate
2. **Esempi**: Includi esempi concreti nel prompt
3. **Formato**: Specifica chiaramente il formato output desiderato

### Ottimizzazione
1. **Batch Size**: Inizia con 5, aumenta se necessario
2. **Soglie**: Regola in base alla qualità desiderata
3. **Modelli**: Testa diversi modelli per il tuo use case

### Qualità
1. **Validazione**: Controlla sempre un campione di risultati
2. **Iterazione**: Migliora il prompt basandoti sui risultati
3. **Metriche**: Monitora le metriche di confidenza
