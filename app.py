# app.py

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Importa le funzioni dal nostro modulo
import analisi_ai as ai

# Carica le variabili di ambiente
load_dotenv()

# --- CONFIGURAZIONE PAGINA E STATO ---
st.set_page_config(layout="wide", page_title="Analisi Interattiva AI", page_icon="📊")

# Inizializzazione session_state
if 'config' not in st.session_state:
    st.session_state.config = {
        'provider_fase1': 'openrouter',
        'model_fase1': 'mistralai/mistral-small-3',
        'provider_fase2': 'openrouter',
        'model_fase2': 'anthropic/claude-3.5-sonnet',
        'provider_report': 'openrouter',
        'model_report': 'anthropic/claude-3.5-sonnet',
        'modalita_analisi': 'pro_contro',
        'temperature': 0.3,
        'soglia_confidenza': 0.7,
        'soglia_secondarie': 0.5,
        'batch_size': 5,
        'max_etichette': 15,
        'batch_mode': True,
        'etichette_multiple': True,
    }
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- SIDEBAR DI CONFIGURAZIONE ---
with st.sidebar:
    st.title("🔧 Configurazione Analisi")
    st.markdown("Imposta i parametri per l'analisi AI.")

    with st.expander("🤖 Modelli AI (Triple-Model)", expanded=True):
        st.subheader("Fase 1: Etichettatura Dinamica")
        st.session_state.config['provider_fase1'] = st.selectbox("Provider Fase 1", ['openrouter', 'ollama', 'openai'], key='p1')
        st.session_state.config['model_fase1'] = st.text_input("Modello Fase 1", value=st.session_state.config['model_fase1'])

        st.subheader("Fase 2: Analisi Avanzata")
        st.session_state.config['provider_fase2'] = st.selectbox("Provider Fase 2", ['openrouter', 'ollama', 'openai'], key='p2')
        st.session_state.config['model_fase2'] = st.text_input("Modello Fase 2", value=st.session_state.config['model_fase2'])

        st.subheader("Fase 3: Report Discorsivo")
        st.session_state.config['provider_report'] = st.selectbox("Provider Report", ['openrouter', 'ollama', 'openai'], key='p3')
        st.session_state.config['model_report'] = st.text_input("Modello Report", value=st.session_state.config['model_report'])

    with st.expander("📊 Parametri Analisi", expanded=True):
        st.session_state.config['modalita_analisi'] = st.selectbox(
            "Modalità Analisi",
            options=list(ai.template_prompts.keys()),
            format_func=lambda x: ai.template_prompts[x]['nome'],
            index=list(ai.template_prompts.keys()).index(st.session_state.config['modalita_analisi'])
        )
        st.session_state.config['temperature'] = st.slider("Temperature", 0.0, 1.0, st.session_state.config['temperature'], 0.1)
        st.session_state.config['soglia_confidenza'] = st.slider("Soglia Confidenza Principale", 0.0, 1.0, st.session_state.config['soglia_confidenza'], 0.05)
        st.session_state.config['soglia_secondarie'] = st.slider("Soglia Confidenza Secondarie", 0.0, 1.0, st.session_state.config['soglia_secondarie'], 0.05)
        st.session_state.config['max_etichette'] = st.slider("Max Etichette Dinamiche", 5, 30, st.session_state.config['max_etichette'], 1)

    with st.expander("⚙️ Elaborazione Batch", expanded=True):
        st.session_state.config['batch_mode'] = st.checkbox("Modalità Batch", value=st.session_state.config['batch_mode'])
        if st.session_state.config['batch_mode']:
            st.session_state.config['batch_size'] = st.slider("Dimensione Batch", 1, 50, st.session_state.config['batch_size'], 1)
            st.info(f"🚀 Con Batch Size {st.session_state.config['batch_size']}, l'analisi sarà circa {st.session_state.config['batch_size']}x più veloce.")

# --- INTERFACCIA PRINCIPALE ---
st.title("📊 Analisi Interattiva di Commenti Excel con AI")
st.markdown("Carica un file Excel, configura l'analisi e ottieni etichette automatiche e report dettagliati.")

# 1. Caricamento File
st.header("1. 📁 Carica il tuo file Excel")
uploaded_file = st.file_uploader("Trascina qui il file o clicca per navigare", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"File '{uploaded_file.name}' caricato con successo! ({df.shape[0]} righe, {df.shape[1]} colonne)")
    st.dataframe(df.head())

    # 2. Selezione Colonna
    st.header("2. 🎯 Seleziona la colonna da analizzare")
    colonna_da_analizzare = st.selectbox(
        "Scegli la colonna contenente i commenti",
        options=df.columns,
        format_func=lambda col: f"{col} ({df[col].notna().sum()} commenti non vuoti)"
    )

    # 3. Avvio Analisi
    st.header("3. 🚀 Avvia l'analisi")
    if st.button("Avvia Analisi Avanzata", type="primary"):
        st.session_state.analysis_results = None # Resetta risultati precedenti
        config = st.session_state.config

        try:
            # Inizializza LLM
            api_key = os.getenv("OPENROUTER_API_KEY") if config['provider_fase1'] == 'openrouter' else os.getenv("OPENAI_API_KEY")
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

            with st.spinner("Inizializzazione modelli AI..."):
                llm_fase1 = ai.inizializza_llm(config['provider_fase1'], config['model_fase1'], api_key, ollama_url, config['temperature'])
                llm_fase2 = ai.inizializza_llm(config['provider_fase2'], config['model_fase2'], api_key, ollama_url, config['temperature'])
                llm_report = ai.inizializza_llm(config['provider_report'], config['model_report'], api_key, ollama_url, config['temperature'])
            st.success("Modelli AI inizializzati.")

            # Pipeline di analisi
            status_text = st.empty()
            progress_bar = st.progress(0)

            # Fase 1: Analisi Globale
            status_text.text("Fase 1/3: Analisi globale per generare etichette dinamiche...")
            prompt_template = ai.template_prompts[config['modalita_analisi']]['prompt']
            etichette_dinamiche, analisi_globale_txt = ai.analizza_colonna_completa(df, colonna_da_analizzare, prompt_template, llm_fase1)
            progress_bar.progress(33)
            st.info(f"Fase 1 completata: {len(etichette_dinamiche)} etichette dinamiche generate.")

            # Fase 2: Etichettatura Batch
            status_text.text("Fase 2/3: Etichettatura dei commenti...")
            def progress_callback(processed, total):
                percent_complete = 66 + (processed / total) * 33
                progress_bar.progress(min(int(percent_complete), 99))
                status_text.text(f"Fase 2/3: Etichettatura dei commenti... ({processed}/{total})")

            risultati_etichettatura = ai.etichetta_con_coefficiente_batch(df, colonna_da_analizzare, etichette_dinamiche, config['modalita_analisi'], llm_fase2, config, progress_callback)
            progress_bar.progress(66)
            st.info("Fase 2 completata: Tutti i commenti sono stati etichettati.")

            # Fase 3: Report e salvataggio
            status_text.text("Fase 3/3: Generazione report e salvataggio...")
            output_dir = ai.create_output_dir(config['modalita_analisi'])
            file_paths = ai.salva_risultati(df, risultati_etichettatura, etichette_dinamiche, analisi_globale_txt, output_dir, config['modalita_analisi'])
            
            df_risultati = pd.read_excel(file_paths['excel'])
            report_discorsivo = ai.genera_report_discorsivo(df_risultati, etichette_dinamiche, config, llm_report)
            progress_bar.progress(100)
            
            # Salva risultati in sessione
            st.session_state.analysis_results = {
                "df_risultati": df_risultati,
                "report_discorsivo": report_discorsivo,
                "file_paths": file_paths,
                "output_dir": output_dir
            }
            
            st.success("🎉 Analisi completata con successo!")
            status_text.empty()
            progress_bar.empty()

        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {e}")
            st.exception(e)


# --- VISUALIZZAZIONE RISULTATI ---
if st.session_state.analysis_results:
    st.header("📈 Risultati dell'Analisi")
    results = st.session_state.analysis_results
    df_risultati = results['df_risultati']

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Riepilogo Grafico", "📄 Report AI", "📋 Dati Etichettati", "💾 Download"])

    with tab1:
        st.subheader("Distribuzione Etichette")
        fig1 = ai.crea_grafico_istogramma_etichette(df_risultati)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Distribuzione Confidenza")
        fig2 = ai.crea_grafico_confidenza_distribuzione(df_risultati)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Report Descrittivo AI")
        st.markdown(results['report_discorsivo'])

    with tab3:
        st.subheader("Anteprima dei dati con etichette")
        st.dataframe(df_risultati)

    with tab4:
        st.subheader("Scarica i file generati")
        st.info(f"I file sono stati salvati nella cartella: `{results['output_dir']}`")
        
        with open(results['file_paths']['excel'], 'rb') as f:
            st.download_button(
                label="📥 Scarica Report Excel (.xlsx)",
                data=f,
                file_name=os.path.basename(results['file_paths']['excel']),
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        with open(results['file_paths']['etichette'], 'rb') as f:
            st.download_button(
                label="📥 Scarica Etichette (.json)",
                data=f,
                file_name=os.path.basename(results['file_paths']['etichette']),
                mime='application/json'
            )