#!/usr/bin/env python3
"""
Test del sistema di progresso modificato nel notebook
"""

def test_progresso_format():
    """Testa il formato del progresso p% numero/totale"""
    
    print("🧪 Test del sistema di progresso modificato")
    print("=" * 50)
    
    # Simula alcuni valori di test
    test_cases = [
        (1, 100),   # 1%
        (4, 100),   # 4% (esempio dell'utente)
        (10, 100),  # 10%
        (25, 100),  # 25%
        (50, 100),  # 50%
        (99, 100),  # 99%
        (100, 100), # 100%
        (3, 20),    # 15%
        (7, 30),    # 23%
    ]
    
    print("Formato del progresso che apparirà nel notebook:")
    print("-" * 50)
    
    for numero_corrente, totale_commenti in test_cases:
        percentuale = int((numero_corrente / totale_commenti) * 100)
        
        # Calcolo della progress bar (fase 2 va da 40% a 80%)
        progress_fase2 = 40 + int((numero_corrente / totale_commenti) * 40)
        
        # Formato che apparirà nel widget fase_label
        fase_text = f"🏷️ FASE 2: Etichettatura {percentuale}% {numero_corrente}/{totale_commenti}"
        
        print(f"{fase_text:<60} | Progress Bar: {progress_fase2}%")
    
    print("\n" + "=" * 50)
    print("✅ Il nuovo sistema mostrerà:")
    print("   - Percentuale esatta (p%)")
    print("   - Numero corrente/totale (4/100)")
    print("   - Progress bar da 40% a 80% per la fase 2")
    print("   - Messaggi ogni 10 commenti nella console")

if __name__ == "__main__":
    test_progresso_format()
