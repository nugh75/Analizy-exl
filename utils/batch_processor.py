"""
⚡ Batch Processing Module for AI Analysis
Modulo ottimizzato per l'etichettatura batch di commenti con AI
"""

import time
import logging
import pandas as pd
import re
from typing import Dict, List, Any, Tuple


def etichetta_con_coefficiente_batch(df: pd.DataFrame, 
                                   etichette_dinamiche: Dict[str, Dict],
                                   colonna_riferimento: str,
                                   tipo_analisi: str,
                                   llm: Any,
                                   ai_provider: str,
                                   soglia_confidenza: float = 0.3,
                                   batch_size: int = 5,
                                   fase_label=None,
                                   progress_bar=None) -> Dict[str, List]:
    """
    Etichetta ogni cella con coefficienti di corrispondenza per tutte le etichette
    VERSIONE OTTIMIZZATA: Raggruppa più commenti per ridurre le chiamate API
    
    Args:
        df: DataFrame con i dati
        etichette_dinamiche: Dizionario delle etichette generate dinamicamente
        colonna_riferimento: Nome della colonna da analizzare
        tipo_analisi: Tipo di analisi da eseguire
        llm: Modello di linguaggio da utilizzare
        ai_provider: Provider AI ('ollama' o 'openrouter')
        soglia_confidenza: Soglia minima per considerare un'etichetta valida
        batch_size: Numero di commenti da processare insieme (1-20)
        fase_label: Widget per mostrare la fase corrente (opzionale)
        progress_bar: Widget progress bar (opzionale)
    
    Returns:
        Dict contenente tutti i risultati dell'etichettatura
    """
    
    logging.info(f"Inizio etichettatura BATCH ottimizzata (batch_size: {batch_size}, soglia: {soglia_confidenza})")
    print(f"🚀 MODALITÀ BATCH ATTIVA: {batch_size} commenti per chiamata API")
    print(f"⚡ Velocizzazione stimata: {batch_size}x rispetto alla modalità singola")
    
    risultati = {
        "etichette_principali": [],
        "coefficienti_principali": [],
        "etichette_secondarie": [],
        "coefficienti_completi": [],
        "confidenza_media": []
    }
    
    # Prepara la lista delle etichette per il prompt
    lista_etichette = "\n".join([
        f"- {nome}: {info['descrizione']}" 
        for nome, info in etichette_dinamiche.items()
    ])
    
    # Inizializza tutti i risultati con None per mantenere l'ordine
    total_rows = len(df)
    for _ in range(total_rows):
        risultati["etichette_principali"].append(None)
        risultati["coefficienti_principali"].append(None)
        risultati["etichette_secondarie"].append(None)
        risultati["coefficienti_completi"].append(None)
        risultati["confidenza_media"].append(None)
    
    # Prima gestisci le righe vuote
    for index, row in df.iterrows():
        if pd.isna(row[colonna_riferimento]):
            risultati["etichette_principali"][index] = "Vuota"
            risultati["coefficienti_principali"][index] = 0.0
            risultati["etichette_secondarie"][index] = ""
            risultati["coefficienti_completi"][index] = "{}"
            risultati["confidenza_media"][index] = 0.0
    
    # Processa i commenti validi in batch
    valid_indices = df[df[colonna_riferimento].notna()].index.tolist()
    
    for batch_start in range(0, len(valid_indices), batch_size):
        batch_end = min(batch_start + batch_size, len(valid_indices))
        batch_indices = valid_indices[batch_start:batch_end]
        batch_commenti = [df.loc[idx, colonna_riferimento] for idx in batch_indices]
        
        # Calcola progresso dettagliato
        batch_progress = batch_end
        percentuale = int((batch_progress / len(valid_indices)) * 100)
        
        # Aggiorna gli indicatori di progresso se disponibili
        if fase_label:
            fase_label.value = f"<b>🏷️ FASE 2: Etichettatura BATCH {percentuale}% {batch_progress}/{len(valid_indices)}</b>"
        
        if progress_bar:
            progress_fase2 = 40 + int((batch_progress / len(valid_indices)) * 40)
            progress_bar.value = progress_fase2
        
        logging.info(f"Processando batch {batch_start//batch_size + 1}: commenti {batch_start+1}-{batch_end} ({percentuale}%)")
        print(f"   ⚡ Batch {batch_start//batch_size + 1}: Analizzando {len(batch_commenti)} commenti insieme...")
        
        # Crea prompt per il batch
        prompt_batch = create_batch_prompt(batch_commenti, lista_etichette, soglia_confidenza)
        
        try:
            # Invoca il modello AI
            if ai_provider.lower() == 'ollama':
                risposta = llm.invoke(prompt_batch)
            else:
                messages = [
                    {"role": "system", "content": f"Sei un analista esperto che calcola coefficienti di corrispondenza per {tipo_analisi}. Analizza sempre TUTTI i commenti forniti."},
                    {"role": "user", "content": prompt_batch}
                ]
                risposta = llm.invoke(messages)
            
            # Parsing della risposta batch
            risultati_batch = parse_batch_response(str(risposta), len(batch_commenti), soglia_confidenza)
            
            # Assegna i risultati agli indici corretti
            for i, idx in enumerate(batch_indices):
                if i < len(risultati_batch):
                    risultato = risultati_batch[i]
                    risultati["etichette_principali"][idx] = risultato["principale"]
                    risultati["coefficienti_principali"][idx] = risultato["coeff_principale"]
                    risultati["etichette_secondarie"][idx] = risultato["secondarie"]
                    risultati["coefficienti_completi"][idx] = risultato["tutti_coefficienti"]
                    risultati["confidenza_media"][idx] = risultato["confidenza_generale"]
                else:
                    # Fallback in caso di errore di parsing
                    risultati["etichette_principali"][idx] = "Errore_Batch"
                    risultati["coefficienti_principali"][idx] = 0.0
                    risultati["etichette_secondarie"][idx] = ""
                    risultati["coefficienti_completi"][idx] = "{}"
                    risultati["confidenza_media"][idx] = 0.0
            
            print(f"   ✅ Batch completato: {len(batch_commenti)} commenti processati")
            
            # Mostra alcuni risultati del batch
            for i, idx in enumerate(batch_indices[:3]):  # Mostra primi 3 risultati
                if i < len(risultati_batch):
                    risultato = risultati_batch[i]
                    print(f"      📝 Riga {idx+1}: {risultato['principale']} ({risultato['coeff_principale']:.2f})")
            
        except Exception as e:
            logging.error(f"Errore nel batch {batch_start//batch_size + 1}: {e}")
            print(f"   ❌ Errore nel batch: {e}")
            
            # Assegna valori di errore a tutto il batch
            for idx in batch_indices:
                risultati["etichette_principali"][idx] = "Errore_Batch"
                risultati["coefficienti_principali"][idx] = 0.0
                risultati["etichette_secondarie"][idx] = ""
                risultati["coefficienti_completi"][idx] = "{}"
                risultati["confidenza_media"][idx] = 0.0
        
        # Pausa più breve tra batch (invece di pausa per ogni commento)
        time.sleep(0.5)
    
    # Calcola statistiche finali
    coefficienti_validi = [c for c in risultati["coefficienti_principali"] if c and c > 0]
    risultati["statistiche_confidenza"] = {
        "media_coefficienti": sum(coefficienti_validi) / len(coefficienti_validi) if coefficienti_validi else 0,
        "alta_confidenza": len([c for c in coefficienti_validi if c >= 0.7]),
        "media_confidenza": len([c for c in coefficienti_validi if 0.4 <= c < 0.7]),
        "bassa_confidenza": len([c for c in coefficienti_validi if 0.1 <= c < 0.4]),
        "molto_bassa": len([c for c in coefficienti_validi if c < 0.1])
    }
    
    print(f"\n🎉 ETICHETTATURA BATCH COMPLETATA!")
    print(f"⚡ Velocizzazione ottenuta: ~{batch_size}x rispetto alla modalità singola")
    print(f"🔢 Batch processati: {(len(valid_indices) + batch_size - 1) // batch_size}")
    print(f"📊 Commenti validi: {len(valid_indices)}/{len(df)}")
    
    logging.info("Etichettatura batch con coefficienti completata")
    return risultati


def create_batch_prompt(batch_commenti: List[str], lista_etichette: str, soglia_confidenza: float) -> str:
    """Crea il prompt per l'analisi batch di più commenti"""
    
    prompt_batch = f"""Analizza questi {len(batch_commenti)} commenti e calcola quanto ognuno si adatta a OGNI etichetta (coefficiente 0.0-1.0).

ETICHETTE DISPONIBILI:
{lista_etichette}

COMMENTI DA ANALIZZARE:
"""
    
    for i, commento in enumerate(batch_commenti, 1):
        prompt_batch += f"COMMENTO_{i}: \"{commento}\"\n"
    
    prompt_batch += f"""
ISTRUZIONI:
1. Per OGNI commento e OGNI etichetta, assegna un coefficiente da 0.0 (nessuna corrispondenza) a 1.0 (perfetta corrispondenza)
2. Sii preciso nella valutazione - usa l'intera scala 0.0-1.0
3. Per ogni commento, identifica l'etichetta principale (coefficiente più alto)
4. Indica anche etichette secondarie significative (sopra {soglia_confidenza})

FORMATO RISPOSTA (ripeti per ogni commento):
=== COMMENTO_1 ===
PRINCIPALE: [nome_etichetta] (coefficiente: 0.XX)
SECONDARIE: [etichetta1] (0.XX), [etichetta2] (0.XX)
TUTTI_COEFFICIENTI: {{"etichetta1": 0.XX, "etichetta2": 0.XX, ...}}
CONFIDENZA_GENERALE: 0.XX

=== COMMENTO_2 ===
PRINCIPALE: [nome_etichetta] (coefficiente: 0.XX)
SECONDARIE: [etichetta1] (0.XX), [etichetta2] (0.XX)
TUTTI_COEFFICIENTI: {{"etichetta1": 0.XX, "etichetta2": 0.XX, ...}}
CONFIDENZA_GENERALE: 0.XX

[continua per tutti i commenti...]"""

    return prompt_batch


def parse_batch_response(risposta: str, num_commenti: int, soglia: float) -> List[Dict[str, Any]]:
    """Parsing specializzato per risposte batch"""
    
    risultati = []
    
    # Dividi la risposta per commenti
    sezioni_commento = re.split(r'=== COMMENTO_\d+ ===', risposta)
    
    # Rimuovi la prima sezione se vuota
    if sezioni_commento and not sezioni_commento[0].strip():
        sezioni_commento.pop(0)
    
    for i in range(num_commenti):
        risultato = {
            "principale": "Incerto",
            "coeff_principale": 0.0,
            "secondarie": "",
            "tutti_coefficienti": "{}",
            "confidenza_generale": 0.0
        }
        
        if i < len(sezioni_commento):
            sezione = sezioni_commento[i]
            
            # Estrae etichetta principale
            match_principale = re.search(r'PRINCIPALE:\s*([^(]+)\s*\(coefficiente:\s*([\d.]+)\)', sezione)
            if match_principale:
                risultato["principale"] = match_principale.group(1).strip()
                risultato["coeff_principale"] = float(match_principale.group(2))
            
            # Estrae etichette secondarie
            match_secondarie = re.search(r'SECONDARIE:\s*(.+)', sezione)
            if match_secondarie:
                risultato["secondarie"] = match_secondarie.group(1).strip()
            
            # Estrae coefficienti completi
            match_coefficienti = re.search(r'TUTTI_COEFFICIENTI:\s*(\{.+\})', sezione)
            if match_coefficienti:
                risultato["tutti_coefficienti"] = match_coefficienti.group(1)
            
            # Estrae confidenza generale
            match_confidenza = re.search(r'CONFIDENZA_GENERALE:\s*([\d.]+)', sezione)
            if match_confidenza:
                risultato["confidenza_generale"] = float(match_confidenza.group(1))
        
        risultati.append(risultato)
    
    return risultati


def calculate_performance_stats(batch_size: int, num_comments: int) -> Dict[str, float]:
    """Calcola statistiche di performance per il batch processing"""
    
    # Tempi stimati (basati su esperienza)
    tempo_per_commento_singolo = 2.5  # secondi
    tempo_per_batch = 2.5  # secondi per batch indipendentemente dalla dimensione
    
    # Calcoli modalità singola
    tempo_singolo = num_comments * tempo_per_commento_singolo
    chiamate_singole = num_comments
    
    # Calcoli modalità batch
    num_batch = (num_comments + batch_size - 1) // batch_size
    tempo_batch = num_batch * tempo_per_batch
    chiamate_batch = num_batch
    
    # Statistiche
    velocizzazione = tempo_singolo / tempo_batch if tempo_batch > 0 else 1
    risparmio_tempo = tempo_singolo - tempo_batch
    risparmio_chiamate = chiamate_singole - chiamate_batch
    risparmio_percentuale = (risparmio_tempo / tempo_singolo * 100) if tempo_singolo > 0 else 0
    
    return {
        "tempo_singolo": tempo_singolo,
        "tempo_batch": tempo_batch,
        "velocizzazione": velocizzazione,
        "risparmio_tempo": risparmio_tempo,
        "risparmio_percentuale": risparmio_percentuale,
        "chiamate_singole": chiamate_singole,
        "chiamate_batch": chiamate_batch,
        "risparmio_chiamate": risparmio_chiamate,
        "num_batch": num_batch
    }


def process_comments_batch(comments: List[str], 
                         prompt: str, 
                         llm: Any, 
                         batch_size: int = 5,
                         progress_callback=None) -> List[str]:
    """
    Processa una lista di commenti usando batch processing
    
    Args:
        comments: Lista di commenti da processare
        prompt: Prompt base per l'analisi
        llm: Modello di linguaggio
        batch_size: Dimensione dei batch
        progress_callback: Funzione per aggiornare il progresso
    
    Returns:
        Lista dei risultati dell'analisi
    """
    
    if not comments:
        return []
    
    risultati = []
    total_batches = (len(comments) + batch_size - 1) // batch_size
    
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        # Crea prompt per il batch
        batch_prompt = create_batch_prompt_simple(batch, prompt)
        
        try:
            # Chiama il modello
            response = llm.invoke(batch_prompt)
            
            # Parsing della risposta
            batch_results = parse_batch_response_simple(response, len(batch))
            risultati.extend(batch_results)
            
            # Aggiorna progresso se callback fornito
            if progress_callback:
                progress_callback(batch_num, total_batches)
            
            # Pausa tra batch per evitare rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logging.error(f"Errore processing batch {batch_num}: {e}")
            # Aggiungi risultati di fallback
            risultati.extend([f"Errore: {str(e)[:50]}" for _ in batch])
    
    return risultati


def create_batch_prompt_simple(comments: List[str], base_prompt: str) -> str:
    """
    Crea un prompt per l'analisi batch semplificata
    
    Args:
        comments: Lista di commenti
        base_prompt: Prompt base
    
    Returns:
        Prompt formattato per il batch
    """
    
    # Numera i commenti
    numbered_comments = "\n".join([
        f"Commento {i+1}: {comment}"
        for i, comment in enumerate(comments)
    ])
    
    return f"""{base_prompt}

COMMENTI DA ANALIZZARE:
{numbered_comments}

FORMATO RISPOSTA:
Commento 1: [etichetta/categoria]
Commento 2: [etichetta/categoria]
{chr(10).join([f"Commento {i+1}: [etichetta/categoria]" for i in range(2, len(comments))])}

Analizza ogni commento separatamente e fornisci una risposta chiara e concisa per ciascuno."""


def parse_batch_response_simple(response: str, expected_count: int) -> List[str]:
    """
    Parsing semplificato della risposta batch
    
    Args:
        response: Risposta del modello
        expected_count: Numero di risultati attesi
    
    Returns:
        Lista di risultati estratti
    """
    
    results = []
    lines = response.split('\n')
    
    # Cerca pattern "Commento X: ..."
    for line in lines:
        line = line.strip()
        if match := re.search(r'Commento\s+\d+:\s*(.+)', line, re.IGNORECASE):
            result = match.group(1).strip()
            if result:
                results.append(result)
    
    # Se il parsing non ha prodotto abbastanza risultati, aggiungi fallback
    while len(results) < expected_count:
        results.append("Non classificato")
    
    # Tronca se troppi risultati
    return results[:expected_count]


def estimate_batch_time(num_comments: int, batch_size: int, time_per_batch: float = 2.0) -> float:
    """
    Stima il tempo necessario per il processing batch
    
    Args:
        num_comments: Numero totale di commenti
        batch_size: Dimensione del batch
        time_per_batch: Tempo stimato per batch in secondi
    
    Returns:
        Tempo stimato in secondi
    """
    
    num_batches = (num_comments + batch_size - 1) // batch_size
    return num_batches * time_per_batch
