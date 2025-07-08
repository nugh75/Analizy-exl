"""
📊 Data Parsers Module
Funzioni per il parsing e l'elaborazione dei dati
"""

import re
import json
import pandas as pd
from typing import Dict, List, Any, Tuple


def parse_etichette_dinamiche(risposta_ai: str) -> Dict[str, Dict[str, str]]:
    """Estrae etichette e descrizioni dalla risposta dell'AI"""
    
    etichette = {}
    linee = risposta_ai.split('\n')
    
    etichetta_corrente = None
    descrizione_corrente = ""
    esempi_correnti = ""
    
    for linea in linee:
        linea = linea.strip()
        if linea.startswith('ETICHETTA:'):
            if etichetta_corrente:
                etichette[etichetta_corrente] = {
                    'descrizione': descrizione_corrente,
                    'esempi': esempi_correnti
                }
            etichetta_corrente = linea.replace('ETICHETTA:', '').strip()
            descrizione_corrente = ""
            esempi_correnti = ""
        elif linea.startswith('DESCRIZIONE:'):
            descrizione_corrente = linea.replace('DESCRIZIONE:', '').strip()
        elif linea.startswith('ESEMPI:'):
            esempi_correnti = linea.replace('ESEMPI:', '').strip()
    
    # Aggiungi l'ultima etichetta
    if etichetta_corrente:
        etichette[etichetta_corrente] = {
            'descrizione': descrizione_corrente,
            'esempi': esempi_correnti
        }
    
    return etichette


def parse_coefficienti_risposta(risposta: str, soglia: float) -> Dict[str, Any]:
    """Estrae coefficienti dalla risposta dell'AI per analisi singola"""
    
    risultato = {
        "principale": "Incerto",
        "coeff_principale": 0.0,
        "secondarie": "",
        "tutti_coefficienti": "{}",
        "confidenza_generale": 0.0
    }
    
    # Estrae etichetta principale
    match_principale = re.search(r'PRINCIPALE:\s*([^(]+)\s*\(coefficiente:\s*([\d.]+)\)', risposta)
    if match_principale:
        risultato["principale"] = match_principale.group(1).strip()
        risultato["coeff_principale"] = float(match_principale.group(2))
    
    # Estrae etichette secondarie
    match_secondarie = re.search(r'SECONDARIE:\s*(.+)', risposta)
    if match_secondarie:
        risultato["secondarie"] = match_secondarie.group(1).strip()
    
    # Estrae coefficienti completi
    match_coefficienti = re.search(r'TUTTI_COEFFICIENTI:\s*(\{.+\})', risposta)
    if match_coefficienti:
        risultato["tutti_coefficienti"] = match_coefficienti.group(1)
    
    # Estrae confidenza generale
    match_confidenza = re.search(r'CONFIDENZA_GENERALE:\s*([\d.]+)', risposta)
    if match_confidenza:
        risultato["confidenza_generale"] = float(match_confidenza.group(1))
    
    return risultato


def validate_dataframe(df: pd.DataFrame, colonna_riferimento: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Valida il DataFrame e la colonna di riferimento
    
    Args:
        df: DataFrame da validare
        colonna_riferimento: Nome della colonna da analizzare
    
    Returns:
        (is_valid: bool, message: str, stats: dict)
    """
    
    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "valid_comments": 0,
        "empty_comments": 0,
        "column_exists": False,
        "data_types": {}
    }
    
    # Verifica esistenza colonna
    if colonna_riferimento not in df.columns:
        return False, f"Colonna '{colonna_riferimento}' non trovata nel DataFrame", stats
    
    stats["column_exists"] = True
    
    # Conta commenti validi e vuoti
    stats["valid_comments"] = df[colonna_riferimento].notna().sum()
    stats["empty_comments"] = df[colonna_riferimento].isna().sum()
    
    # Tipi di dati per ogni colonna
    stats["data_types"] = {col: str(df[col].dtype) for col in df.columns}
    
    # Validazione minima
    if stats["valid_comments"] == 0:
        return False, f"Nessun commento valido trovato nella colonna '{colonna_riferimento}'", stats
    
    if stats["valid_comments"] < 3:
        return False, f"Troppo pochi commenti validi ({stats['valid_comments']}) per un'analisi significativa", stats
    
    return True, f"DataFrame valido: {stats['valid_comments']} commenti pronti per l'analisi", stats


def clean_text_data(df: pd.DataFrame, colonna_riferimento: str) -> pd.DataFrame:
    """
    Pulisce i dati testuali nel DataFrame
    
    Args:
        df: DataFrame da pulire
        colonna_riferimento: Colonna contenente i testi
    
    Returns:
        DataFrame pulito
    """
    
    df_cleaned = df.copy()
    
    # Rimuovi spazi extra e caratteri speciali problematici
    df_cleaned[colonna_riferimento] = df_cleaned[colonna_riferimento].astype(str)
    df_cleaned[colonna_riferimento] = df_cleaned[colonna_riferimento].str.strip()
    
    # Sostituisci stringhe vuote con NaN
    df_cleaned[colonna_riferimento] = df_cleaned[colonna_riferimento].replace('', pd.NA)
    df_cleaned[colonna_riferimento] = df_cleaned[colonna_riferimento].replace('nan', pd.NA)
    
    return df_cleaned


def extract_sample_data(df: pd.DataFrame, colonna_riferimento: str, n_samples: int = 10) -> List[str]:
    """
    Estrae campioni di dati per anteprima
    
    Args:
        df: DataFrame sorgente
        colonna_riferimento: Colonna da campionare
        n_samples: Numero di campioni da estrarre
    
    Returns:
        Lista di campioni di testo
    """
    
    valid_data = df[df[colonna_riferimento].notna()][colonna_riferimento]
    
    if len(valid_data) == 0:
        return []
    
    # Prendi un campione rappresentativo
    sample_size = min(n_samples, len(valid_data))
    samples = valid_data.head(sample_size).tolist()
    
    return samples


def format_analysis_results(risultati: Dict[str, List], etichette_dinamiche: Dict[str, Dict]) -> pd.DataFrame:
    """
    Formatta i risultati dell'analisi in un DataFrame strutturato
    
    Args:
        risultati: Dizionario con i risultati dell'etichettatura
        etichette_dinamiche: Dizionario delle etichette generate
    
    Returns:
        DataFrame formattato con i risultati
    """
    
    df_results = pd.DataFrame({
        'Etichetta_Principale': risultati['etichette_principali'],
        'Coefficiente_Principale': risultati['coefficienti_principali'],
        'Etichette_Secondarie': risultati['etichette_secondarie'],
        'Confidenza_Generale': risultati['confidenza_media'],
        'Coefficienti_Completi': risultati['coefficienti_completi']
    })
    
    # Aggiungi descrizioni delle etichette
    df_results['Descrizione_Etichetta'] = df_results['Etichetta_Principale'].map(
        lambda x: etichette_dinamiche.get(x, {}).get('descrizione', 'N/A') if x in etichette_dinamiche else 'N/A'
    )
    
    # Aggiungi esempi delle etichette
    df_results['Esempi_Etichetta'] = df_results['Etichetta_Principale'].map(
        lambda x: etichette_dinamiche.get(x, {}).get('esempi', 'N/A') if x in etichette_dinamiche else 'N/A'
    )
    
    return df_results


def calculate_analysis_statistics(risultati: Dict[str, List]) -> Dict[str, Any]:
    """
    Calcola statistiche sull'analisi completata
    
    Args:
        risultati: Dizionario con i risultati dell'etichettatura
    
    Returns:
        Dizionario con le statistiche
    """
    
    coefficienti = risultati['coefficienti_principali']
    coefficienti_validi = [c for c in coefficienti if c and c > 0]
    
    if not coefficienti_validi:
        return {
            "total_analyzed": len(coefficienti),
            "valid_results": 0,
            "average_confidence": 0.0,
            "quality_distribution": {
                "high": 0, "medium": 0, "low": 0, "very_low": 0
            }
        }
    
    # Distribuzione qualità
    high_quality = len([c for c in coefficienti_validi if c >= 0.7])
    medium_quality = len([c for c in coefficienti_validi if 0.4 <= c < 0.7])
    low_quality = len([c for c in coefficienti_validi if 0.1 <= c < 0.4])
    very_low_quality = len([c for c in coefficienti_validi if c < 0.1])
    
    # Etichette più frequenti
    etichette = risultati['etichette_principali']
    etichette_valide = [e for e in etichette if e not in ['Vuota', 'Errore', 'Incerto', 'Errore_Batch']]
    
    from collections import Counter
    top_etichette = Counter(etichette_valide).most_common(10)
    
    return {
        "total_analyzed": len(coefficienti),
        "valid_results": len(coefficienti_validi),
        "average_confidence": sum(coefficienti_validi) / len(coefficienti_validi),
        "quality_distribution": {
            "high": high_quality,
            "medium": medium_quality, 
            "low": low_quality,
            "very_low": very_low_quality
        },
        "top_labels": top_etichette,
        "completion_rate": len(coefficienti_validi) / len(coefficienti) if coefficienti else 0
    }
