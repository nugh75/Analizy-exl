"""
Test di integrazione per il sistema completo
"""
import sys
import os
import tempfile
import json

# Aggiungi la directory utils al path per gli import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

def create_test_excel():
    """Crea un file Excel di test"""
    try:
        import pandas as pd
        
        # Dati di test
        data = {
            'commenti': [
                'Prodotto eccellente, molto soddisfatto',
                'Servizio clienti lento e poco disponibile',
                'Buona qualità ma prezzo alto',
                'Consegna veloce, prodotto come descritto',
                'Problema con il prodotto, chiedo rimborso'
            ],
            'id': [1, 2, 3, 4, 5],
            'data': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
        }
        
        df = pd.DataFrame(data)
        
        # Salva in file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            return tmp.name
            
    except ImportError:
        print("⚠️  Pandas non disponibile per creare file di test")
        return None


def test_complete_workflow():
    """Test del workflow completo"""
    print("🧪 Test workflow completo...")
    
    # 1. Crea file di test
    test_file = create_test_excel()
    if not test_file:
        print("❌ Impossibile creare file di test")
        return False
    
    try:
        # 2. Test caricamento file
        from data_parsers import load_excel_file, get_column_info
        
        df = load_excel_file(test_file)
        if df is None:
            print("❌ Caricamento file fallito")
            return False
        print("✅ File caricato correttamente")
        
        # 3. Test info colonne
        columns = get_column_info(df)
        if 'commenti' not in columns:
            print("❌ Colonna commenti non trovata")
            return False
        print("✅ Colonne identificate correttamente")
        
        # 4. Test configurazione
        from config_manager import load_config, validate_config
        
        config = load_config()
        if not validate_config(config):
            print("❌ Configurazione non valida")
            return False
        print("✅ Configurazione valida")
        
        # 5. Test batch processing (simulato)
        from batch_processor import create_batch_prompt
        
        comments = df['commenti'].tolist()[:3]  # Prime 3 per test
        prompt = create_batch_prompt(comments, "Analizza sentiment")
        
        if not prompt or len(prompt) < 50:
            print("❌ Prompt batch non creato correttamente")
            return False
        print("✅ Batch prompt creato")
        
        print("🎉 Workflow completo: SUCCESSO")
        return True
        
    except Exception as e:
        print(f"❌ Errore nel workflow: {e}")
        return False
        
    finally:
        # Pulisci file temporaneo
        if test_file and os.path.exists(test_file):
            os.unlink(test_file)


def test_error_handling():
    """Test gestione errori"""
    print("🧪 Test gestione errori...")
    
    try:
        # Test file non esistente
        from data_parsers import load_excel_file
        
        result = load_excel_file("file_non_esistente.xlsx")
        if result is not None:
            print("❌ Dovrebbe ritornare None per file non esistente")
            return False
        print("✅ Gestione file non esistente corretta")
        
        # Test configurazione mancante
        from config_manager import load_config
        
        # Temporaneamente rinomina .env se esiste
        env_backup = None
        if os.path.exists('.env'):
            env_backup = '.env.backup'
            os.rename('.env', env_backup)
        
        try:
            config = load_config()
            # Dovrebbe caricare valori di default
            if not isinstance(config, dict):
                print("❌ Configurazione default non caricata")
                return False
            print("✅ Configurazione default caricata")
        finally:
            # Ripristina .env se esisteva
            if env_backup and os.path.exists(env_backup):
                os.rename(env_backup, '.env')
        
        print("🎉 Gestione errori: SUCCESSO")
        return True
        
    except Exception as e:
        print(f"❌ Errore nei test: {e}")
        return False


def test_performance_benchmark():
    """Test benchmark performance"""
    print("🧪 Test benchmark performance...")
    
    try:
        import time
        
        # Simula processing di molti commenti
        comments = [f"Commento di test numero {i}" for i in range(50)]
        
        # Test batch vs singolo (simulato)
        start_time = time.time()
        
        # Simula batch processing
        batch_size = 5
        batches = len(comments) // batch_size
        for i in range(batches):
            # Simula elaborazione batch
            time.sleep(0.01)  # 10ms per batch
        
        batch_time = time.time() - start_time
        
        # Simula processing singolo
        start_time = time.time()
        for comment in comments:
            # Simula elaborazione singola
            time.sleep(0.005)  # 5ms per commento
        
        single_time = time.time() - start_time
        
        speedup = single_time / batch_time if batch_time > 0 else 0
        
        print(f"📊 Batch time: {batch_time:.3f}s")
        print(f"📊 Single time: {single_time:.3f}s") 
        print(f"📊 Speedup: {speedup:.2f}x")
        
        if speedup > 1:
            print("✅ Batch processing più veloce")
        else:
            print("⚠️  Batch processing non più veloce (normale per test simulato)")
        
        print("🎉 Benchmark: COMPLETATO")
        return True
        
    except Exception as e:
        print(f"❌ Errore benchmark: {e}")
        return False


def run_all_tests():
    """Esegui tutti i test di integrazione"""
    print("🚀 Avvio test di integrazione completi")
    print("=" * 50)
    
    tests = [
        ("Workflow Completo", test_complete_workflow),
        ("Gestione Errori", test_error_handling), 
        ("Benchmark Performance", test_performance_benchmark)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📋 RIEPILOGO RISULTATI:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n📊 Risultato finale: {passed}/{total} test passati")
    
    if passed == total:
        print("🎉 TUTTI I TEST PASSATI!")
        return True
    else:
        print("⚠️  Alcuni test falliti - controllare la configurazione")
        return False


if __name__ == "__main__":
    run_all_tests()
