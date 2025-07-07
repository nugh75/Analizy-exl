import pandas as pd
import logging
import os
import time
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Estrai la chiave API di OpenAI dall'ambiente
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise ValueError("La chiave API di OpenAI non è stata trovata. Assicurati che sia presente nel file .env.")

# Configura il modello OpenAI tramite LangChain usando ChatOpenAI con il modello gpt-4o-mini
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=openai_api_key)

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("operazioni_log.log"),
        logging.StreamHandler()
    ]
)

# Funzione per creare la cartella di output, includendo il tipo di analisi nel nome
def create_output_dir(tipo_analisi):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f'{tipo_analisi}_output_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Cartella di output creata: {output_dir}")
    return output_dir

# Funzione per leggere il file Excel
def load_excel(file_path, colonna_riferimento):
    try:
        df = pd.read_excel(file_path)
        logging.info(f"File Excel '{file_path}' caricato con successo.")
        return df, colonna_riferimento
    except Exception as e:
        logging.error(f"Errore durante il caricamento del file Excel: {e}")
        raise

# Funzione per analizzare complessivamente i commenti
def analizza_commenti(commenti, tipo_analisi):
    prompt_template = ChatPromptTemplate.from_template(
        f"""Il seguente testo descrive vari aspetti di un progetto scolastico. 
        La tua attività è analizzare attentamente il testo e identificare tutte le categorie o etichette pertinenti che descrivono i concetti chiave presenti nel testo.

        Per ogni categoria o etichetta, segui queste regole:
        1.  Etichette uniche : Assicurati che ogni etichetta sia distintiva e non sovrapposta a un'altra. Non utilizzare sinonimi o parole troppo simili per etichette diverse.
           - Evita termini troppo generici come "comunicazione" e "collaborazione" se possono essere sostituiti con etichette più specifiche.
           - Non ripetere concetti con variazioni minime. Ogni etichetta deve descrivere un aspetto chiaramente differente.

        2.  Cattura tutti gli aspetti : Esplora tutte le sfumature del testo, anche quelle meno evidenti. Cerca di estrarre il maggior numero di concetti chiave, facendo attenzione a quelli impliciti o meno evidenti, senza lasciare nulla di importante fuori.
           - Se un concetto o un'idea viene trattato da diverse prospettive, crea etichette separate per ciascuna prospettiva.
           - Se ci sono aspetti collegati a più livelli (es. "Collaborazione tra insegnanti" e "Collaborazione con genitori"), crea etichette separate.

        3.  Etichette concise ma descrittive : Ogni etichetta deve essere breve (una o due parole) ma rappresentare chiaramente un concetto completo.
           - Usa termini specifici quando possibile. Ad esempio, preferisci "Collaborazione Insegnanti-Genitori" piuttosto che solo "Collaborazione".
           - Non includere termini vaghi come "buona" o "efficace" nelle etichette.

        4.  Massimo 20 etichette : Non produrre più di 20 etichette. Se hai molti concetti simili, scegli quello che meglio li rappresenta in modo univoco.

        5.  Spiegazione di ogni etichetta : Per ciascuna etichetta, fornisci una spiegazione dettagliata del perché hai scelto quel termine, cosa rappresenta e quali aspetti del testo riflette.
           - La spiegazione deve chiarire come l'etichetta si differenzia dalle altre e quale parte specifica del testo la giustifica.

        Ecco il testo da analizzare:

        Commenti: {{commenti}}
        """
    )
    
    prompt_completo = prompt_template.format(commenti=commenti)
    messages_completi = [{"role": "system", "content": f"Sei un assistente che analizza i {tipo_analisi} di un progetto scolastico."},
                         {"role": "user", "content": prompt_completo}]
    
    try:
        logging.info(f"Inizio dell'analisi complessiva dei {tipo_analisi}.")
        sintesi = llm.invoke(messages_completi)
        logging.info(f"Analisi complessiva dei {tipo_analisi} completata.")
        return sintesi.content
    except Exception as e:
        logging.error(f"Errore durante l'analisi complessiva dei {tipo_analisi}: {e}")
        raise

# Funzione per etichettare i singoli commenti
def etichetta_commenti(df, spiegazioni, colonna_riferimento, tipo_analisi):
    etichette_analisi = []
    prompt_template = ChatPromptTemplate.from_template(
        f"""Analizza il seguente commento che descrive i {tipo_analisi} del progetto 'Scuole Aperte'. 
        Usa i seguenti {tipo_analisi}, con i rispettivi titoli e spiegazioni, per selezionare una o più etichette appropriate per questo commento:
        
        {tipo_analisi.capitalize()}: {{spiegazioni}}
        
        Commento: {{commento}}
        """
    )
    
    for index, row in df.iterrows():
        commento = row[colonna_riferimento]
        
        if pd.isna(commento):
            etichette_analisi.append("Vuota")
            continue
        
        logging.info(f"Etichettatura del commento con ID {row['id']}: {commento}")
        
        prompt = prompt_template.format(spiegazioni=spiegazioni, commento=commento)
        messages = [{"role": "system", "content": f"Sei un assistente che etichetta i {tipo_analisi} di un progetto scolastico."},
                    {"role": "user", "content": prompt}]
        
        try:
            etichetta_risposta = llm.invoke(messages)
            etichette_selezionate = etichetta_risposta.content.strip()
            etichette_analisi.append(etichette_selezionate)
            logging.info(f"Etichetta assegnata: {etichette_selezionate}")
        except Exception as e:
            logging.error(f"Errore durante l'etichettatura: {e}")
            etichette_analisi.append("Errore")
        
        time.sleep(1)
    
    return etichette_analisi

# Funzione principale che esegue tutto il processo
def esegui_analisi(file_path, tipo_analisi="analisi", colonna_riferimento="ANALISI"):
    # Crea cartella di output con il tipo di analisi nel nome
    output_dir = create_output_dir(tipo_analisi)

    # Carica il file Excel
    df, colonna_riferimento = load_excel(file_path, colonna_riferimento)

    # Analizza i commenti
    commenti_totali = "\n".join(df[colonna_riferimento].dropna().astype(str))
    sintesi_analisi = analizza_commenti(commenti_totali, tipo_analisi)

    # Salva la sintesi
    sintesi_file_path = os.path.join(output_dir, f'sintesi_{tipo_analisi}.txt')
    with open(sintesi_file_path, 'w') as file:
        file.write(sintesi_analisi)
    
    logging.info(f"Sintesi dei {tipo_analisi} salvata in '{sintesi_file_path}'.")

    # Estrai spiegazioni e etichette principali
    spiegazioni_analisi = "\n".join([line.strip() for line in sintesi_analisi.split('\n') if line.strip()])

    # Etichettatura dei commenti
    etichette = etichetta_commenti(df, spiegazioni_analisi, colonna_riferimento, tipo_analisi)
    
    # Aggiungi etichette al DataFrame
    df['Etichetta'] = etichette

    # Salva il risultato in Excel
    excel_file_path = os.path.join(output_dir, f'report_{tipo_analisi}.xlsx')
    df[['id', colonna_riferimento, 'Etichetta']].to_excel(excel_file_path, index=False)
    
    logging.info(f"Report completo salvato in '{excel_file_path}'.")
    print(f"Analisi completata. Report completo salvato in '{excel_file_path}'.")

# Esegui l'analisi generica
esegui_analisi("/Users/desi76/Library/CloudStorage/OneDrive-UniversitadegliStudiRomaTre/Scuole aperte file non condivisi/ostacoli.xlsx", tipo_analisi="ostacoli", colonna_riferimento="OSTACOLI")
