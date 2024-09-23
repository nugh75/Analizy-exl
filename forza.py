import pandas as pd
import logging
import os
import time  # Importiamo il modulo time per aggiungere pause
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from docx import Document
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

# Crea la cartella con data e ora
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = f'output_{timestamp}'
os.makedirs(output_dir, exist_ok=True)

logging.info(f"Cartella di output creata: {output_dir}")

# Fase 1: Analisi complessiva dei punti di forza con etichette (titoli) e spiegazioni
prompt_template_1 = ChatPromptTemplate.from_template(
    """Analizza il seguente insieme di commenti che descrivono i punti di forza del progetto 'Scuole Aperte'. 
    Per ogni punto di forza, genera un titolo (una o due parole) che sarà l'etichetta. Fornisci poi una spiegazione dettagliata di quel punto di forza. 
    Limita il numero di punti di forza a un massimo di 20.
    
    Commenti: {commenti}
    """
)

# Fase 2: Etichettatura di ciascun commento con le etichette (titoli) derivanti dalla Fase 1, utilizzando anche le spiegazioni
prompt_template_2 = ChatPromptTemplate.from_template(
    """Analizza il seguente commento che descrive i punti di forza del progetto 'Scuole Aperte'. 
    Usa i seguenti punti di forza, con i rispettivi titoli e spiegazioni, per selezionare una o più etichette appropriate per questo commento:
    
    Punti di forza: {punti_di_forza}
    
    Commento: {commento}
    """
)

# Leggi il file Excel
file_path = "/Users/desi76/Library/CloudStorage/OneDrive-UniversitadegliStudiRomaTre/Scuole aperte file non condivisi/punti_di_forza.xlsx"
try:
    df = pd.read_excel(file_path)
    logging.info(f"File Excel '{file_path}' caricato con successo.")
except Exception as e:
    logging.error(f"Errore durante il caricamento del file Excel: {e}")
    raise

# Converti tutti i valori in stringhe prima di concatenare
commenti_totali = "\n".join(df['FORZA'].dropna().astype(str))

# Fase 1: Analisi complessiva dei punti di forza
try:
    logging.info("Inizio dell'analisi complessiva dei punti di forza.")
    
    # Crea il prompt per l'analisi complessiva
    prompt_completo = prompt_template_1.format(commenti=commenti_totali)

    messages_completi = [{"role": "system", "content": "Sei un assistente che analizza i punti di forza di un progetto scolastico."},
                         {"role": "user", "content": prompt_completo}]
    
    # Invoca GPT per generare la sintesi complessiva
    sintesi_punti_di_forza = llm.invoke(messages_completi)
    
    # Log del successo dell'analisi complessiva
    logging.info("Analisi complessiva dei punti di forza completata con successo.")
    
    # Salva la sintesi in un file di testo
    sintesi_file_path = os.path.join(output_dir, 'sintesi_punti_di_forza.txt')
    with open(sintesi_file_path, 'w') as file:
        file.write(sintesi_punti_di_forza.content)
    
    logging.info(f"Sintesi dei punti di forza salvata in '{sintesi_file_path}'.")
    
    # Estrai le etichette (titoli) e spiegazioni dai punti di forza (massimo 20)
    etichette_principali = [line.split(":")[0].strip() for line in sintesi_punti_di_forza.content.split('\n') if ':' in line][:20]
    spiegazioni_punti_di_forza = "\n".join([line.strip() for line in sintesi_punti_di_forza.content.split('\n') if line.strip()])
    
    logging.info(f"Le 20 etichette principali sono: {etichette_principali}")
    
    # Pausa di 2 secondi tra le fasi
    time.sleep(2)
    
except Exception as e:
    logging.error(f"Errore durante l'analisi complessiva dei punti di forza: {e}")
    raise

# Fase 2: Etichettatura di ciascun commento con le 20 etichette principali, includendo le spiegazioni
etichette_punti_di_forza = []
try:
    for index, row in df.iterrows():
        commento = row['FORZA']
        
        if pd.isna(commento):
            etichette_punti_di_forza.append("Vuota")
            continue
        
        logging.info(f"Etichettatura del commento con ID {row['id']}: {commento}")
        
        # Crea il prompt per etichettare ciascun commento, includendo titoli e spiegazioni
        prompt = prompt_template_2.format(punti_di_forza=spiegazioni_punti_di_forza, commento=commento)

        messages = [{"role": "system", "content": "Sei un assistente che etichetta i commenti di un progetto scolastico."},
                    {"role": "user", "content": prompt}]
        
        # Invoca GPT per selezionare le etichette appropriate
        etichetta_risposta = llm.invoke(messages)
        
        # Aggiungi solo le etichette al DataFrame
        etichette_selezionate = etichetta_risposta.content.strip()
        etichette_punti_di_forza.append(etichette_selezionate)
        logging.info(f"Etichetta assegnata: {etichette_selezionate}")
        
        # Pausa di 1 secondo tra ogni chiamata per evitare il rate limit
        time.sleep(1)
        
except Exception as e:
    logging.error(f"Errore durante l'etichettatura dei commenti: {e}")
    raise

# Aggiungi solo le etichette al DataFrame
df['Etichetta'] = etichette_punti_di_forza

# Salvataggio dei risultati in un file Excel
excel_file_path = os.path.join(output_dir, 'report_punti_di_forza.xlsx')
try:
    # Salva solo il DataFrame con le etichette nel file Excel
    df[['id', 'FORZA', 'Etichetta']].to_excel(excel_file_path, index=False)
    logging.info(f"Report completo salvato in '{excel_file_path}'.")
except Exception as e:
    logging.error(f"Errore durante il salvataggio del file Excel: {e}")
    raise

logging.info("Processo completato con successo.")
print(f"Analisi completata. Report completo salvato in '{excel_file_path}'.")
