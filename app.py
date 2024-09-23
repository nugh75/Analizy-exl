import pandas as pd
import logging
import os
from langchain_openai import ChatOpenAI  # Corretto: usa ChatOpenAI
from langchain.prompts import ChatPromptTemplate  # Corretto: usa ChatPromptTemplate
from dotenv import load_dotenv

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Estrai la chiave API di OpenAI dall'ambiente
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise ValueError("La chiave API di OpenAI non è stata trovata. Assicurati che sia presente nel file .env.")

# Configura il modello OpenAI tramite LangChain usando ChatOpenAI con il modello gpt-4o-mini
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=openai_api_key)

# Configurazione del logging per mostrare anche nel terminale
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("operazioni_log.log"),
        logging.StreamHandler()  # Aggiungi il log sul terminale
    ]
)

# Log dell'inizio del processo
logging.info("Inizio del processo di analisi dei punti di forza")

# Fase 1: Estrazione dei punti di forza da ciascun commento
prompt_template_1 = ChatPromptTemplate.from_template(
    """Analizza il seguente commento che descrive i punti di forza di un progetto scolastico. Riassumi i punti principali emersi:
    {commento}
    """
)

# Fase 2: Analisi dei punti di forza complessivi
prompt_template_2 = ChatPromptTemplate.from_template(
    """Ecco un elenco di punti di forza estratti da vari commenti di insegnanti su un progetto scolastico:
    {punti_di_forza}
    Analizza questi punti di forza, raggruppa quelli simili e fai una sintesi dei temi principali emersi.
    """
)

# Leggi il file Excel
file_path = "/Users/desi76/Library/CloudStorage/OneDrive-UniversitadegliStudiRomaTre/Scuole aperte file non condivisi/punti_di_forza.xlsx"  # Cambia con il percorso corretto
try:
    df = pd.read_excel(file_path)
    logging.info(f"File Excel '{file_path}' caricato con successo.")
except Exception as e:
    logging.error(f"Errore durante il caricamento del file Excel: {e}")
    raise

# Lista per salvare i risultati dell'analisi (Fase 1)
report_punti_di_forza = []

# Fase 1: Itera su ogni riga della colonna 'FORZA' e estrai i punti di forza
for index, row in df.iterrows():
    id_commento = row['id']  # ID del commento
    commento = row['FORZA']  # Testo del commento da analizzare
    
    # Verifica se la cella del commento è vuota
    if pd.isna(commento):
        logging.info(f"Cella vuota per l'ID {id_commento}, saltato.")
        report_punti_di_forza.append("Cella vuota")
        continue
    
    try:
        # Log dell'inizio dell'analisi del commento
        logging.info(f"Analisi del commento con ID {id_commento}: {commento}")
        
        # Crea il prompt per la prima fase
        prompt = prompt_template_1.format(commento=commento)

        # Crea la struttura del messaggio richiesta da OpenAI
        messages = [{"role": "system", "content": "Sei un assistente che analizza i punti di forza di un progetto scolastico."},
                    {"role": "user", "content": prompt}]
        
        # Invoca l'analisi tramite LangChain/OpenAI per estrarre i punti di forza
        result = llm.invoke(messages)  # Usa il metodo `invoke` al posto di `__call__`
        
        # Aggiungi il risultato alla lista dei punti di forza
        report_punti_di_forza.append(result.content)  # Usa `content` per accedere al testo
        
        # Log del successo dell'analisi del commento
        logging.info(f"Risultato dell'analisi per l'ID {id_commento}: {result.content}")
    except Exception as e:
        # Log di eventuali errori durante l'analisi
        logging.error(f"Errore durante l'analisi del commento con ID {id_commento}: {e}")
        report_punti_di_forza.append(f"Errore nell'analisi: {e}")

# Crea un nuovo DataFrame per il report dei punti di forza estratti
df_report = pd.DataFrame({
    'ID': df['id'],  # Colonna con l'ID
    'Commento Originale': df['FORZA'],  # Colonna con i commenti originali
    'Punti di Forza': report_punti_di_forza
})

# Fase 2: Analisi dei punti di forza complessivi
punti_di_forza_complessivi = "\n".join([p for p in report_punti_di_forza if p != "Cella vuota"])

try:
    logging.info("Inizio dell'analisi complessiva dei punti di forza.")
    
    # Crea il prompt per la seconda fase
    prompt_completo = prompt_template_2.format(punti_di_forza=punti_di_forza_complessivi)

    # Crea la struttura del messaggio per la seconda fase
    messages_completi = [{"role": "system", "content": "Sei un assistente che analizza i punti di forza di un progetto scolastico."},
                         {"role": "user", "content": prompt_completo}]
    
    # Invoca l'analisi di LangChain/OpenAI per raggruppare e sintetizzare i punti di forza
    sintesi_punti_di_forza = llm.invoke(messages_completi)  # Usa `invoke`
    
    # Log del successo dell'analisi complessiva
    logging.info("Analisi complessiva dei punti di forza completata con successo.")
except Exception as e:
    logging.error(f"Errore durante l'analisi complessiva dei punti di forza: {e}")
    raise

# Salva il report in un nuovo file Excel (Fase 1)
try:
    df_report.to_excel('report_punti_di_forza.xlsx', index=False)
    logging.info("Report della Fase 1 salvato con successo in 'report_punti_di_forza.xlsx'.")
except Exception as e:
    logging.error(f"Errore durante il salvataggio del report della Fase 1: {e}")
    raise

# Salva la sintesi dei punti di forza (Fase 2) in un file di testo
try:
    with open('sintesi_punti_di_forza.txt', 'w') as file:
        file.write(sintesi_punti_di_forza.content)  # Usa `content` per accedere al testo
    logging.info("Sintesi dei punti di forza della Fase 2 salvata in 'sintesi_punti_di_forza.txt'.")
except Exception as e:
    logging.error(f"Errore durante il salvataggio della sintesi dei punti di forza: {e}")
    raise

logging.info("Processo completato con successo.")
print("Analisi completata. Report della Fase 1 salvato in 'report_punti_di_forza.xlsx'.")
print("Sintesi dei punti di forza della Fase 2 salvata in 'sintesi_punti_di_forza.txt'.")
