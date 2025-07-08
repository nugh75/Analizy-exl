"""
⚙️ Configuration Manager Module
Gestione delle configurazioni e parametri dell'applicazione
"""

import json
import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class AnalysisConfig:
    """Classe per gestire la configurazione dell'analisi"""
    
    # Parametri base
    soglia_confidenza: float = 0.3
    etichette_multiple: bool = True
    soglia_secondarie: float = 0.4
    modalita_analisi: str = 'balanced'
    max_etichette_dinamiche: int = 20
    
    # Parametri batch processing
    batch_mode: bool = True
    batch_size: int = 5
    
    # Parametri AI
    ai_provider: str = 'ollama'
    ai_model: str = 'llama3.2'
    temperature: float = 0.7
    
    # Parametri avanzati
    pause_between_requests: float = 1.0
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def validate(self) -> Tuple[bool, str]:
        """Valida la configurazione"""
        
        # Validazioni parametri base
        if not 0.1 <= self.soglia_confidenza <= 0.9:
            return False, "Soglia confidenza deve essere tra 0.1 e 0.9"
        
        if not 0.1 <= self.soglia_secondarie <= 0.9:
            return False, "Soglia secondarie deve essere tra 0.1 e 0.9"
        
        if self.modalita_analisi not in ['strict', 'balanced', 'loose']:
            return False, "Modalità analisi deve essere 'strict', 'balanced' o 'loose'"
        
        if not 5 <= self.max_etichette_dinamiche <= 30:
            return False, "Max etichette dinamiche deve essere tra 5 e 30"
        
        # Validazioni batch processing
        if not 1 <= self.batch_size <= 20:
            return False, "Batch size deve essere tra 1 e 20"
        
        # Validazioni AI
        if self.ai_provider not in ['ollama', 'openrouter']:
            return False, "Provider AI deve essere 'ollama' o 'openrouter'"
        
        if not 0.0 <= self.temperature <= 2.0:
            return False, "Temperature deve essere tra 0.0 e 2.0"
        
        return True, "Configurazione valida"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte la configurazione in dizionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisConfig':
        """Crea configurazione da dizionario"""
        return cls(**data)
    
    def save_to_file(self, filepath: str) -> bool:
        """Salva configurazione su file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore salvataggio configurazione: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'AnalysisConfig':
        """Carica configurazione da file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Errore caricamento configurazione: {e}")
            return cls()  # Ritorna configurazione default


def get_template_prompts() -> Dict[str, Dict[str, str]]:
    """Restituisce i template dei prompt predefiniti"""
    
    return {
        'feedback_studenti': {
            'nome': '📚 Analisi Feedback Studenti',
            'prompt': '''Analizza questi commenti di feedback degli studenti e identifica:

1. **Aspetti positivi** del corso/insegnamento
2. **Aree di miglioramento** suggerite 
3. **Difficoltà specifiche** incontrate
4. **Richieste particolari** degli studenti
5. **Valutazioni generali** dell'esperienza

Crea etichette che catturino sia i sentimenti (positivo/negativo/neutro) che i temi specifici (contenuti, metodologia, organizzazione, supporto).'''
        },
        
        'valutazione_progetti': {
            'nome': '🎯 Valutazione Progetti Scolastici',
            'prompt': '''Analizza questi commenti di valutazione sui progetti e identifica:

1. **Qualità del lavoro** svolto
2. **Creatività e originalità** mostrate
3. **Competenze tecniche** dimostrate
4. **Collaborazione e teamwork**
5. **Rispetto delle consegne** e tempistiche
6. **Aree di eccellenza** e punti di forza
7. **Aspetti da migliorare** per il futuro

Genera etichette che riflettano sia il livello di performance che le competenze specifiche valutate.'''
        },
        
        'problemi_apprendimento': {
            'nome': '🧠 Identificazione Difficoltà di Apprendimento',
            'prompt': '''Analizza questi commenti per identificare difficoltà di apprendimento e:

1. **Tipi di difficoltà** riscontrate (comprensione, memoria, attenzione, etc.)
2. **Materie specifiche** con maggiori problemi
3. **Strategie compensative** già utilizzate
4. **Supporti necessari** per il miglioramento
5. **Progressi osservati** nel tempo
6. **Fattori ambientali** che influenzano l'apprendimento

Crea etichette diagnostiche che aiutino a comprendere le esigenze specifiche di ogni studente.'''
        },
        
        'comportamento_classe': {
            'nome': '👥 Analisi Comportamento in Classe',
            'prompt': '''Analizza questi commenti sul comportamento degli studenti e identifica:

1. **Interazioni sociali** con compagni e insegnanti
2. **Livelli di partecipazione** alle attività
3. **Rispetto delle regole** e disciplina
4. **Motivazione e interesse** mostrati
5. **Problematiche comportamentali** specifiche
6. **Punti di forza caratteriali** da valorizzare
7. **Interventi educativi** necessari

Genera etichette che catturino sia comportamenti positivi che aree di intervento educativo.'''
        },
        
        'generico': {
            'nome': '🔍 Analisi Generica Commenti',
            'prompt': '''Analizza questi commenti in modo generico e identifica:

1. **Temi principali** emergenti dal testo
2. **Sentiment generale** (positivo, negativo, neutro)
3. **Argomenti ricorrenti** e pattern
4. **Criticità evidenziate** nei commenti
5. **Aspetti positivi** menzionati
6. **Richieste o suggerimenti** presenti
7. **Categorie tematiche** naturali nel dataset

Crea etichette flessibili che si adattino al contenuto specifico presente nei dati.'''
        }
    }


def get_quality_thresholds(modalita: str) -> Dict[str, float]:
    """Restituisce le soglie di qualità per modalità"""
    
    thresholds = {
        'strict': {
            'high_quality': 0.8,
            'medium_quality': 0.6,
            'low_quality': 0.3,
            'very_low': 0.0
        },
        'balanced': {
            'high_quality': 0.7,
            'medium_quality': 0.4,
            'low_quality': 0.1,
            'very_low': 0.0
        },
        'loose': {
            'high_quality': 0.6,
            'medium_quality': 0.3,
            'low_quality': 0.05,
            'very_low': 0.0
        }
    }
    
    return thresholds.get(modalita, thresholds['balanced'])


def get_batch_recommendations(num_comments: int) -> Dict[str, Any]:
    """Fornisce raccomandazioni per la dimensione del batch"""
    
    if num_comments <= 50:
        return {
            'recommended_size': 3,
            'reason': 'Dataset piccolo - priorità qualità',
            'alternative_sizes': [1, 5],
            'estimated_time_reduction': '3x'
        }
    elif num_comments <= 200:
        return {
            'recommended_size': 5,
            'reason': 'Dataset medio - bilanciamento ottimale',
            'alternative_sizes': [3, 8],
            'estimated_time_reduction': '5x'
        }
    elif num_comments <= 500:
        return {
            'recommended_size': 8,
            'reason': 'Dataset grande - priorità efficienza',
            'alternative_sizes': [5, 12],
            'estimated_time_reduction': '8x'
        }
    else:
        return {
            'recommended_size': 12,
            'reason': 'Dataset molto grande - massima velocità',
            'alternative_sizes': [8, 15, 20],
            'estimated_time_reduction': '12x'
        }


def create_output_directory(tipo_analisi: str, base_path: str = "output") -> str:
    """Crea directory di output per i risultati"""
    
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_path, f"{tipo_analisi}_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def validate_environment() -> Tuple[bool, List[str]]:
    """Valida l'ambiente e le dipendenze"""
    
    issues = []
    
    # Verifica variabili d'ambiente
    required_env_vars = ['AI_PROVIDER']
    for var in required_env_vars:
        if not os.getenv(var):
            issues.append(f"Variabile d'ambiente {var} non impostata")
    
    # Verifica OpenRouter se necessario
    if os.getenv('AI_PROVIDER', '').lower() == 'openrouter':
        if not os.getenv('OPENROUTER_API_KEY'):
            issues.append("OPENROUTER_API_KEY richiesta per OpenRouter")
    
    # Verifica dipendenze Python (solo check importazione)
    try:
        import pandas
        import requests
        import json
    except ImportError as e:
        issues.append(f"Dipendenza mancante: {e}")
    
    return len(issues) == 0, issues


def get_default_config() -> AnalysisConfig:
    """Restituisce la configurazione predefinita"""
    return AnalysisConfig()
