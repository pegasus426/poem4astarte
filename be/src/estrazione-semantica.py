#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import docx
import sys
import re
import os
from typing import List, Dict, Tuple

def leggi_docx(percorso_file: str) -> Dict[str, str]:
    """
    Legge un file DOCX e restituisce un dizionario con titoli e testo dei paragrafi.
    
    Args:
        percorso_file: Percorso del file DOCX da leggere
        
    Returns:
        Un dizionario dove le chiavi sono i titoli dei paragrafi e i valori sono i contenuti
    """
    try:
        doc = docx.Document(percorso_file)
        paragrafi = {}
        titolo_corrente = "Introduzione"
        testo_corrente = []
        
        for paragrafo in doc.paragraphs:
            testo = paragrafo.text.strip()
            if not testo:
                continue
                
            # Assumiamo che i titoli siano in stile grassetto
            if any(run.bold for run in paragrafo.runs):
                # Salva il paragrafo precedente prima di passare al nuovo titolo
                if testo_corrente:
                    paragrafi[titolo_corrente] = " ".join(testo_corrente)
                    testo_corrente = []
                titolo_corrente = testo
            else:
                testo_corrente.append(testo)
        
        # Aggiungi l'ultimo paragrafo
        if testo_corrente:
            paragrafi[titolo_corrente] = " ".join(testo_corrente)
            
        return paragrafi
    except Exception as e:
        print(f"Errore nella lettura del file DOCX: {e}")
        sys.exit(1)

def estrazione_saltatoria(testo: str, salto: int = 50) -> List[str]:
    """
    Esegue un'estrazione saltatoria con il passo specificato (tipo Weissmandel).
    
    Args:
        testo: Il testo da cui estrarre
        salto: Il numero di caratteri da saltare tra un'estrazione e l'altra
        
    Returns:
        Lista di caratteri estratti usando il metodo saltatorio
    """
    # Rimuovi spazi e normalizza il testo
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    
    risultato = []
    caratteri_estratti = []
    
    # Se il testo è troppo corto per applicare il salto
    if len(testo_pulito) < salto:
        return ["Testo troppo corto per estrazione saltatoria"]
    
    for indice in range(0, len(testo_pulito), salto):
        if indice < len(testo_pulito):
            caratteri_estratti.append(testo_pulito[indice])
    
    # Raggruppa in gruppi di 3 caratteri per formare "parole"
    for i in range(0, len(caratteri_estratti), 3):
        gruppo = caratteri_estratti[i:i+3]
        if len(gruppo) == 3:  # Prendi solo gruppi completi di 3
            risultato.append(''.join(gruppo))
    
    return risultato

def incroci_semantici(testo: str) -> List[str]:
    """
    Identifica incroci semantici nel testo (tipo Michael Drosnin).
    Questa è una semplificazione del metodo ELS (Equidistant Letter Sequences)
    utilizzato da Drosnin nella sua analisi della Torah.
    
    Args:
        testo: Il testo da analizzare
        
    Returns:
        Lista di termini trovati attraverso incroci semantici
    """
    # Lista di parole significative da cercare (esempio)
    parole_chiave = ["dio", "vita", "morte", "amore", "pace", "guerra", 
                     "luce", "buio", "bene", "male", "verità", "fede"]
    
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    risultati = []
    
    # Cerca sequenze ELS per ogni parola chiave
    for parola in parole_chiave:
        for salto in range(2, 50):  # Prova diversi salti
            for posizione_iniziale in range(salto):
                sequenza = ""
                for i in range(posizione_iniziale, len(testo_pulito), salto):
                    sequenza += testo_pulito[i]
                
                if parola in sequenza:
                    risultati.append(f"{parola} (salto: {salto})")
                    break  # Passa alla prossima parola chiave dopo il primo match
    
    return risultati

def crea_output_formattato(risultati: Dict[str, Dict[str, List[str]]]) -> str:
    """
    Crea un output formattato dei risultati.
    
    Args:
        risultati: Dizionario con i risultati delle estrazioni
        
    Returns:
        Stringa con output formattato
    """
    output = []
    
    for titolo, estrazioni in risultati.items():
        output.append(f"\n{'=' * 60}")
        output.append(f"TITOLO: {titolo}")
        output.append(f"{'=' * 60}")
        
        output.append("\nESTRAZIONE SALTATORIA (TIPO WEISSMANDEL):")
        output.append("-" * 40)
        if estrazioni["saltatoria"]:
            output.append(" | ".join(estrazioni["saltatoria"]))
        else:
            output.append("Nessun risultato")
            
        output.append("\nINCROCI SEMANTICI (TIPO DROSNIN):")
        output.append("-" * 40)
        if estrazioni["semantici"]:
            output.append("\n".join(estrazioni["semantici"]))
        else:
            output.append("Nessun risultato")
    
    return "\n".join(output)

def main():
    """Funzione principale del programma"""
    if len(sys.argv) != 3:
        print("Utilizzo: python estrazione_semantica.py <percorso_file.docx> salto_num")
        sys.exit(1)
    
    percorso_file = sys.argv[1]
    salto = sys.argv[2]
    
    if not os.path.exists(percorso_file):
        print(f"Errore: Il file '{percorso_file}' non esiste.")
        sys.exit(1)
        
    if not percorso_file.endswith('.docx'):
        print("Errore: Il file deve essere in formato DOCX.")
        sys.exit(1)
    
    print(f"Analisi del file: {percorso_file}")
    print("Elaborazione in corso...\n")
    
    # Leggi il documento
    paragrafi = leggi_docx(percorso_file)
    
    # Dizionario per i risultati
    risultati = {}
    
    # Elabora ogni paragrafo
    #for titolo, testo in paragrafi.items():
     #   risultati[titolo] = {
      #      "saltatoria": estrazione_saltatoria(testo, salto),
       #     "semantici": incroci_semantici(testo)
       # }

    # Appiattisci il testo di tutti i paragrafi in una stringa rimuovendo gli spazi
    testo_completo = " ".join(paragrafi.values())
    
    # Estrazione saltatoria
    risultati["Tutto il testo"] = {
        "saltatoria": estrazione_saltatoria(testo_completo, salto),
        "semantici": incroci_semantici(testo_completo)
    }
    
    print("Analisi completata!")
    print("\n")
    
    # Salva i risultati in un file di testo
    nome_file_output = os.path.splitext(percorso_file)[0] + "_risultati.txt"
    with open(nome_file_output, 'w', encoding='utf-8') as f:
        f.write(output_formattato)
    
    print(f"\nI risultati sono stati salvati nel file: {nome_file_output}")
    
    # Mostra i risultati
    output_formattato = crea_output_formattato(risultati)
    print(output_formattato)
    
    # Salva i risultati in un file di testo
    nome_file_output = os.path.splitext(percorso_file)[0] + "_risultati.txt"
    with open(nome_file_output, 'w', encoding='utf-8') as f:
        f.write(output_formattato)
    
    print(f"\nI risultati sono stati salvati nel file: {nome_file_output}")

if __name__ == "__main__":
    main()
