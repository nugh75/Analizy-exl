# analisi_ai.py

import pandas as pd
import logging
import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("operazioni_log.log"),
        logging.StreamHandler()
    ]
)

# --- DEFINIZIONE TEMPLATE DI PROMPT ---
# (Questa sezione contiene il dizionario template_prompts del notebook)
template_prompts = {
    "sentiment_analysis": {
        "nome": "📊 Sentiment Analysis",
        "descrizione": "Analizza il sentiment (positivo, negativo, neutro) dei commenti",
        "prompt": "..." # Inserire il prompt completo dal notebook
    },
    "pro_contro": {
        "nome": "⚖️ Analisi Pro e Contro",
        "descrizione": "Identifica vantaggi, svantaggi, benefici e criticità",
        "prompt": "..." # Inserire il prompt completo dal notebook
    },
    # ... Inserire qui tutti gli altri template dal notebook ...
    "uso_ia_educazione": {
        "nome": "🤖 Analisi Uso IA in Educazione",
        "descrizione": "Analisi di vantaggi, svantaggi, emozioni e comportamenti nell'uso dell'IA educativa",
        "prompt": "..." # Inserire il prompt completo dal notebook
    }
}
# Nota: per brevità, i prompt non sono espansi qui, ma dovrebbero essere copiati integralmente.

# --- FUNZIONI DI INIZIALIZZAZIONE LLM ---

def inizializza_llm(provider, model_name, api_key, base_url, temperatura=0.3):
    """Inizializza un LLM specifico."""
    try:
        if provider == 'ollama':
            # Assicurarsi che l'URL base sia corretto e il servizio attivo
            return Ollama(
                model=model_name,
                temperature=temperatura,
                num_predict=2048,
                base_url=base_url
            )
        elif provider == 'openrouter':
            return ChatOpenAI(
                model=model_name,
                temperature=temperatura,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        elif provider == 'openai':
            return ChatOpenAI(
                model=model_name,
                temperature=temperatura,
                api_key=api_key
            )
        else:
            raise ValueError(f"Provider non supportato: {provider}")
    except Exception as e:
        logging.error(f"❌ Errore inizializzazione LLM {provider}/{model_name}: {e}")
        raise

# --- FUNZIONI DI ANALISI E PIPELINE ---

def create_output_dir(tipo_analisi):
    """Crea una cartella di output univoca per i risultati."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f'output/{tipo_analisi}_output_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Cartella di output creata: {output_dir}")
    return output_dir

def analizza_colonna_completa(df, colonna_riferimento, prompt_template, llm):
    """Analizza l'intera colonna per generare etichette dinamiche."""
    logging.info(f"Inizio analisi globale della colonna '{colonna_riferimento}'")
    commenti_validi = df[colonna_riferimento].dropna().astype(str).tolist()
    if not commenti_validi:
        raise ValueError("Nessun commento valido trovato nella colonna specificata.")

    testo_completo = "\n".join(commenti_validi)
    
    prompt_etichette = f"""Analizza TUTTO il seguente testo che contiene {len(commenti_validi)} commenti.
OBIETTIVO: Genera un dizionario completo di etichette dinamiche basate sui contenuti REALI di questi commenti.
ISTRUZIONI:
1. Leggi tutti i commenti per identificare temi, pattern e concetti ricorrenti.
2. Crea etichette specifiche e pertinenti al contenuto effettivo.
3. Ogni etichetta deve rappresentare un concetto distintivo presente nei dati.
4. Fornisci una descrizione dettagliata per ogni etichetta.
5. Includi anche etichette per concetti minoritari ma significativi.
FORMATO RICHIESTO: Per ogni etichetta, scrivi:
ETICHETTA: [nome_breve]
DESCRIZIONE: [spiegazione dettagliata di cosa rappresenta]
ESEMPI: [parole chiave o frasi tipiche]
---
TEMPLATE ANALISI:
{prompt_template}
TESTO DA ANALIZZARE:
{testo_completo}
Genera massimo 25 etichette dinamiche basate sui contenuti reali."""

    risposta_etichette = llm.invoke(prompt_etichette)
    etichette_dinamiche = parse_etichette_dinamiche(str(risposta_etichette))
    logging.info(f"Analisi globale completata: {len(etichette_dinamiche)} etichette generate")
    return etichette_dinamiche, str(risposta_etichette)

def parse_etichette_dinamiche(risposta_ai):
    """Estrae etichette e descrizioni dalla risposta dell'AI."""
    etichette = {}
    sezioni = risposta_ai.split('---')
    for sezione in sezioni:
        etichetta = re.search(r'ETICHETTA:\s*(.*)', sezione)
        descrizione = re.search(r'DESCRIZIONE:\s*(.*)', sezione)
        esempi = re.search(r'ESEMPI:\s*(.*)', sezione)
        if etichetta and descrizione:
            nome_etichetta = etichetta.group(1).strip()
            etichette[nome_etichetta] = {
                'descrizione': descrizione.group(1).strip(),
                'esempi': esempi.group(1).strip() if esempi else ""
            }
    return etichette

def etichetta_con_coefficiente_batch(df, colonna_riferimento, etichette_dinamiche, tipo_analisi, llm, config, progress_callback=None):
    """Etichetta i commenti in batch per ottimizzare le chiamate API."""
    batch_size = config['batch_size']
    soglia_confidenza = config['soglia_confidenza']
    logging.info(f"Inizio etichettatura BATCH (size: {batch_size}, soglia: {soglia_confidenza})")

    risultati_finali = [None] * len(df)
    commenti_validi_df = df[df[colonna_riferimento].notna()].copy()
    
    lista_etichette = "\n".join([f"- {nome}: {info['descrizione']}" for nome, info in etichette_dinamiche.items()])

    total_valid = len(commenti_validi_df)
    processed_count = 0

    for i in range(0, total_valid, batch_size):
        batch_df = commenti_validi_df.iloc[i:i + batch_size]
        batch_commenti = batch_df[colonna_riferimento].tolist()

        commenti_prompt_str = ""
        for j, commento in enumerate(batch_commenti):
            commenti_prompt_str += f"COMMENTO_{j+1}: \"{commento}\"\n"
        
        prompt_batch = f"""Analizza questi {len(batch_commenti)} commenti e calcola quanto ognuno si adatta a OGNI etichetta.
ETICHETTE DISPONIBILI:
{lista_etichette}
COMMENTI DA ANALIZZARE:
{commenti_prompt_str}
ISTRUZIONI:
1. Per OGNI commento e OGNI etichetta, assegna un coefficiente da 0.0 a 1.0.
2. Per ogni commento, identifica l'etichetta principale (coefficiente più alto).
3. Indica anche etichette secondarie (sopra {soglia_confidenza}).
FORMATO RISPOSTA (ripeti per ogni commento):
=== COMMENTO_1 ===
PRINCIPALE: [nome_etichetta] (coefficiente: 0.XX)
SECONDARIE: [etichetta1] (0.XX), [etichetta2] (0.XX)
TUTTI_COEFFICIENTI: {{\"etichetta1\": 0.XX, ...}}
CONFIDENZA_GENERALE: 0.XX
[continua per tutti i commenti...]"""
        
        try:
            risposta = llm.invoke(prompt_batch)
            risultati_batch = parse_batch_response(str(risposta), len(batch_commenti))
            
            for j, risultato_parsing in enumerate(risultati_batch):
                original_index = batch_df.index[j]
                risultati_finali[original_index] = risultato_parsing
        
        except Exception as e:
            logging.error(f"Errore nel batch a partire da indice {i}: {e}")
            for j in range(len(batch_df)):
                original_index = batch_df.index[j]
                risultati_finali[original_index] = {
                    "principale": "Errore_Batch", "coeff_principale": 0.0,
                    "secondarie": "", "tutti_coefficienti": "{}", "confidenza_generale": 0.0
                }

        processed_count += len(batch_df)
        if progress_callback:
            progress_callback(processed_count, total_valid)
            
    # Gestione righe vuote
    for i in range(len(df)):
        if pd.isna(df.loc[i, colonna_riferimento]):
             risultati_finali[i] = {
                "principale": "Vuota", "coeff_principale": 0.0,
                "secondarie": "", "tutti_coefficienti": "{}", "confidenza_generale": 0.0
            }
            
    return risultati_finali

import re
def parse_batch_response(risposta, num_commenti):
    """Parsing specializzato per risposte batch."""
    risultati = []
    sezioni_commento = re.split(r'=== COMMENTO_\d+ ===', risposta)
    if sezioni_commento and not sezioni_commento[0].strip():
        sezioni_commento.pop(0)

    for i in range(num_commenti):
        risultato = {"principale": "Incerto", "coeff_principale": 0.0, "secondarie": "", "tutti_coefficienti": "{}", "confidenza_generale": 0.0}
        if i < len(sezioni_commento):
            sezione = sezioni_commento[i]
            match_p = re.search(r'PRINCIPALE:\s*([^(]+)\s*\(coefficiente:\s*([\d.]+)\)', sezione)
            if match_p:
                risultato["principale"] = match_p.group(1).strip()
                risultato["coeff_principale"] = float(match_p.group(2))
            
            match_s = re.search(r'SECONDARIE:\s*(.+)', sezione)
            if match_s:
                risultato["secondarie"] = match_s.group(1).strip()
            
            match_c = re.search(r'TUTTI_COEFFICIENTI:\s*(\{.*\})', sezione, re.DOTALL)
            if match_c:
                risultato["tutti_coefficienti"] = match_c.group(1)
            
            match_conf = re.search(r'CONFIDENZA_GENERALE:\s*([\d.]+)', sezione)
            if match_conf:
                risultato["confidenza_generale"] = float(match_conf.group(1))
        risultati.append(risultato)
    return risultati

def salva_risultati(df_originale, risultati_etichettatura, etichette_dinamiche, analisi_globale, output_dir, tipo_analisi):
    """Salva i risultati dell'analisi in file Excel e JSON."""
    df_risultati = df_originale.copy()
    df_risultati['Etichetta_Principale'] = [r['principale'] for r in risultati_etichettatura]
    df_risultati['Coefficiente_Principale'] = [r['coeff_principale'] for r in risultati_etichettatura]
    df_risultati['Etichette_Secondarie'] = [r['secondarie'] for r in risultati_etichettatura]
    df_risultati['Confidenza_Generale'] = [r['confidenza_generale'] for r in risultati_etichettatura]
    df_risultati['Coefficienti_Completi'] = [r['tutti_coefficienti'] for r in risultati_etichettatura]

    # Salva file
    paths = {}
    paths['excel'] = os.path.join(output_dir, f'report_avanzato_{tipo_analisi}.xlsx')
    paths['etichette'] = os.path.join(output_dir, f'etichette_dinamiche_{tipo_analisi}.json')
    paths['analisi_globale'] = os.path.join(output_dir, f'analisi_globale_{tipo_analisi}.txt')

    df_risultati.to_excel(paths['excel'], index=False)
    with open(paths['etichette'], 'w', encoding='utf-8') as f:
        json.dump(etichette_dinamiche, f, ensure_ascii=False, indent=2)
    with open(paths['analisi_globale'], 'w', encoding='utf-8') as f:
        f.write(analisi_globale)

    logging.info(f"Risultati avanzati salvati in {output_dir}")
    return paths

def genera_report_discorsivo(df_risultati, etichette_dinamiche, config, llm):
    """Genera un report narrativo utilizzando l'AI."""
    logging.info("Generazione report discorsivo AI...")
    
    stats_confidenza = df_risultati['Coefficiente_Principale'][df_risultati['Coefficiente_Principale'] > 0].describe().to_dict()
    conteggi_etichette = Counter(df_risultati['Etichetta_Principale'][df_risultati['Etichetta_Principale'] != 'Vuota']).most_common(5)
    
    prompt_report = f"""Analizza questi risultati di etichettatura automatica e genera un report descrittivo professionale.
CONTESTO DELL'ANALISI:
- Tipo di analisi: {config['modalita_analisi']}
- Commenti analizzati: {df_risultati[df_risultati['Etichetta_Principale'] != 'Vuota'].shape[0]} / {len(df_risultati)}
ETICHETTE DINAMICHE GENERATE ({len(etichette_dinamiche)} totali):
{json.dumps(etichette_dinamiche, indent=2, ensure_ascii=False)}
STATISTICHE DI QUALITÀ (Coefficiente Principale):
{json.dumps(stats_confidenza, indent=2)}
TOP 5 ETICHETTE PIÙ FREQUENTI:
{conteggi_etichette}
RICHIESTA:
Genera un report professionale di 3-4 paragrafi che includa:
1. SINTESI GENERALE: Panoramica dei risultati e della qualità dell'analisi.
2. ANALISI TEMATICA: Discussione delle etichette più significative.
3. VALUTAZIONE QUALITATIVA: Commento sulla distribuzione della confidenza.
4. RACCOMANDAZIONI: Suggerimenti per l'utilizzo di questi risultati."""

    report_content = llm.invoke(prompt_report)
    return str(report_content)

# --- FUNZIONI PER GRAFICI ---

def crea_grafico_istogramma_etichette(df_risultati, top_n=15):
    """Crea un istogramma interattivo delle etichette più frequenti."""
    etichette_freq = df_risultati['Etichetta_Principale'][df_risultati['Etichetta_Principale'] != 'Vuota'].value_counts().nlargest(top_n).sort_values()
    fig = px.bar(etichette_freq, x=etichette_freq.values, y=etichette_freq.index, orientation='h',
                 title=f'Distribuzione delle Top {len(etichette_freq)} Etichette',
                 labels={'x': 'Numero di Occorrenze', 'y': 'Etichette'},
                 text=etichette_freq.values)
    fig.update_layout(template='plotly_white', height=max(400, len(etichette_freq) * 30))
    return fig

def crea_grafico_confidenza_distribuzione(df_risultati):
    """Crea un istogramma della distribuzione delle confidenze."""
    confidenze = df_risultati['Coefficiente_Principale'][df_risultati['Coefficiente_Principale'] > 0]
    fig = px.histogram(confidenze, nbins=20, title='Distribuzione Livelli di Confidenza',
                       labels={'value': 'Livello di Confidenza', 'count': 'Numero di Commenti'})
    media_conf = confidenze.mean()
    fig.add_vline(x=media_conf, line_dash="dash", line_color="red", annotation_text=f"Media: {media_conf:.3f}")
    fig.update_layout(template='plotly_white')
    return fig