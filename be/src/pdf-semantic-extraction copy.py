#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
import math
from typing import List, Dict, Tuple
import html
import PyPDF2
from io import StringIO
import nltk
from nltk.corpus import words

# Scarica il dataset di parole se non è già presente
nltk.download("words")

# Filtra solo le parole italiane con più di 3 lettere
parole_italiane = [word for word in words.words() if len(word) > 3 and word.isalpha()]

# Stampa le prime 10 parole per verifica
print(parole_italiane[:10])

from spellchecker import SpellChecker

# Inizializza lo spell checker in italiano
spell = SpellChecker(language="it")

# Ottieni la lista delle parole
parole_italiane = [word for word in spell.word_frequency.keys() if len(word) > 3]
#parole italiano tutte to lowercase
parole_italiane = [word.lower() for word in parole_italiane]
# Stampa un'anteprima delle parole
print(parole_italiane[:10])


def leggi_pdf(percorso_file: str) -> Dict[str, str]:
    """
    Legge un file PDF e restituisce un dizionario con titoli e testo dei paragrafi.
    
    Args:
        percorso_file: Percorso del file PDF da leggere
        
    Returns:
        Un dizionario dove le chiavi sono i titoli dei paragrafi e i valori sono i contenuti
    """
    try:
        with open(percorso_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            paragrafi = {}
            titolo_corrente = "Introduzione"
            testo_corrente = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                testo_pagina = page.extract_text()
                
                # Dividi il testo in righe
                linee = testo_pagina.split('\n')
                
                for linea in linee:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    # Euristica per identificare titoli: testo breve, tutto maiuscolo, o finisce con ":"
                    if (len(linea) < 50 and (linea.isupper() or linea.endswith(':') or 
                                            linea.endswith('.') and len(linea.split()) <= 5)):
                        # Salva il paragrafo precedente prima di passare al nuovo titolo
                        if testo_corrente:
                            paragrafi[titolo_corrente] = " ".join(testo_corrente)
                            testo_corrente = []
                        titolo_corrente = linea.rstrip(':.')
                    else:
                        testo_corrente.append(linea)
            
            # Aggiungi l'ultimo paragrafo
            if testo_corrente:
                paragrafi[titolo_corrente] = " ".join(testo_corrente)
                
            return paragrafi
    except Exception as e:
        print(f"Errore nella lettura del file PDF: {e}")
        sys.exit(1)

def estrazione_saltatoria(testo: str, salto: int = 50) -> Tuple[List[str], List[int]]:
    """
    Esegue un'estrazione saltatoria con il passo specificato (tipo Weissmandel).
    Filtra solo le parole presenti nel dizionario italiano.
    
    Args:
        testo: Il testo da cui estrarre
        salto: Il numero di caratteri da saltare tra un'estrazione e l'altra
        
    Returns:
        Tupla con lista di parole estratte e lista di indici dei caratteri nel testo originale
    """
    # Rimuovi spazi e normalizza il testo
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    # Rimuovi punteggiatura e caratteri non alfanumerici
    testo_pulito = re.sub(r'[^\w\s]', '', testo_pulito)
        
    risultato = []
    indici_estratti = []
    
    # Se il testo è troppo corto per applicare il salto
    if len(testo_pulito) < salto:
        return ["Testo troppo corto per estrazione saltatoria"], []
    
    # Estrai caratteri con il salto specificato
    caratteri_estratti = []
    indici_caratteri = []
    
    for indice in range(0, len(testo_pulito), salto):
        if indice < len(testo_pulito):
            caratteri_estratti.append(testo_pulito[indice])
            indici_caratteri.append(indice)
    
    # Crea una stringa con tutti i caratteri estratti
    stringa_estratta = ''.join(caratteri_estratti)
    
    # Cerca parole italiane nella stringa estratta
    parole_trovate = []
    indici_parole = []
    
    for parola in parole_italiane:
        parola = re.sub(r'\s+', '', parola).lower()
        # Rimuovi punteggiatura e caratteri non alfanumerici
        parola = re.sub(r'[^\w\s]', '', parola)
        
        # Cerca tutte le occorrenze della parola nella stringa estratta
        for match in re.finditer(parola, stringa_estratta):
            inizio, fine = match.span()
            
            # Ottieni gli indici originali nel testo per questa parola
            indici_originali = indici_caratteri[inizio:fine]
            
            # Aggiungi la parola e i suoi indici alle liste dei risultati
            parole_trovate.append(parola)
            indici_parole.append(indici_originali)
    
    return parole_trovate, indici_parole

def incroci_semantici(testo: str, salto: int) -> Tuple[List[str], Dict[str, List[Tuple[int, int, List[int]]]]]:
    """
    Identifica incroci semantici nel testo (tipo Michael Drosnin).
    
    Args:
        testo: Il testo da analizzare
        
    Returns:
        Tupla con lista di risultati e dizionario con dettagli delle occorrenze
    """
    # Lista di parole significative da cercare (esempio)
    parole_chiave = parole_italiane
    
        # Rimuovi spazi e normalizza il testo
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    #rimuovi punteggiatura e caratteri non alfanunerici
    testo_pulito = re.sub(r'[^\w\s]', '', testo_pulito)
    risultati = []
    dettagli_occorrenze = {}
    
    # Cerca sequenze ELS per ogni parola chiave
    for parola in parole_chiave:
        for salto2 in range(salto, salto+3):  # Prova diversi salti
            for posizione_iniziale in range(salto2):
                sequenza = ""
                indici = []
                for i in range(posizione_iniziale, len(testo_pulito), salto2):
                    sequenza += testo_pulito[i]
                    indici.append(i)
                
                if parola in sequenza:
                    risultati.append(f"{parola} (salto: {salto2})")
                    
                    # Trova l'indice di inizio della parola nella sequenza
                    indice_inizio_seq = sequenza.find(parola)
                    # Calcola gli indici corrispondenti nel testo originale
                    indici_parola = indici[indice_inizio_seq:indice_inizio_seq+len(parola)]
                    
                    # Memorizza i dettagli di questa occorrenza
                    if parola not in dettagli_occorrenze:
                        dettagli_occorrenze[parola] = []
                    
                    dettagli_occorrenze[parola].append((salto2, posizione_iniziale, indici_parola))
                    break  # Passa alla prossima parola chiave dopo il primo match
    
    return risultati, dettagli_occorrenze
def crea_output_formattato(risultati: Dict[str, Dict[str, List[str]]]) -> str:
    """
    Crea un output formattato in testo dei risultati.
    
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
        if estrazioni["saltatoria_ordinata"]:
            output.append(" | ".join(estrazioni["saltatoria_ordinata"]))
        else:
            output.append("Nessun risultato")
            
        output.append("\nINCROCI SEMANTICI (TIPO DROSNIN):")
        output.append("-" * 40)
        if estrazioni["semantici"]:
            output.append("\n".join(estrazioni["semantici"]))
        else:
            output.append("Nessun risultato")
    
    return "\n".join(output)

def crea_output_html(paragrafi: Dict[str, str], risultati_estesi: Dict[str, Dict[str, any]]) -> str:
    """
    Crea un output HTML formattato dei risultati con visualizzazione grafica.
    
    Args:
        paragrafi: Dizionario con titoli e testi dei paragrafi
        risultati_estesi: Dizionario con risultati delle estrazioni e dettagli
        
    Returns:
        Stringa con output HTML
    """
    html_output = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estrazione Semantica - Risultati</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        header {
            background-color: #28364d;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            margin: 0;
            font-size: 2.2em;
        }
        h2 {
            color: #28364d;
            border-bottom: 2px solid #28364d;
            padding-bottom: 5px;
            margin-top: 40px;
        }
        h3 {
            color: #2c3e50;
            margin-top: 30px;
        }
        .section {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .matrice-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        .matrice {
            border-collapse: collapse;
            font-family: monospace;
            font-size: 14px;
            margin: 0 auto;
        }
        .matrice th {
            background-color: #f0f0f0;
            font-weight: bold;
            padding: 5px;
            text-align: center;
            min-width: 25px;
        }
        .matrice td {
            border: 1px solid #ddd;
            padding: 5px;
            text-align: center;
            min-width: 25px;
            position: relative;
        }
        .matrice td.saltatory {
            background-color: rgba(76, 175, 80, 0.3);
            color: black;
            font-weight: bold;
        }
        .matrice td.semantic {
            background-color: rgba(33, 150, 243, 0.3);
            color: black;
            font-weight: bold;
        }
        .matrice td.saltatory-semantic {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.5) 0%, rgba(33, 150, 243, 0.5) 100%);
            color: black;
            font-weight: bold;
        }
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
            justify-content: center;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
        .green {
            background-color: rgba(76, 175, 80, 0.3);
        }
        .blue {
            background-color: rgba(33, 150, 243, 0.3);
        }
        .mixed {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.5) 0%, rgba(33, 150, 243, 0.5) 100%);
        }
        .result-word {
            display: inline-block;
            background-color: #e8f5e9;
            border-radius: 4px;
            padding: 8px 15px;
            margin: 5px;
            font-weight: bold;
            color: #1b5e20;
            box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
        }
        .result-semantic {
            display: inline-block;
            background-color: #e3f2fd;
            border-radius: 4px;
            padding: 8px 15px;
            margin: 5px;
            font-weight: bold;
            color: #0d47a1;
            box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
        }
        .results-container {
            margin: 20px 0;
            text-align: center;
        }
        .coordenadas {
            font-size: 10px;
            color: #666;
            position: absolute;
            top: 1px;
            right: 1px;
        }
        .subtitle {
            color: #777;
            font-style: italic;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <header>
        <h1>Estrazione Semantica - Risultati</h1>
    </header>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color green"></div>
            <span>Estrazione Saltatoria (50-50-50)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color blue"></div>
            <span>Incroci Semantici (Drosnin)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color mixed"></div>
            <span>Entrambi i metodi</span>
        </div>
    </div>
    """
    
    for titolo, testo in paragrafi.items():
        risultati = risultati_estesi.get("testo completo unificato senza titoli", {})
        indici_saltatoria = risultati.get("indici_saltatoria", [])
        indici_semantici = risultati.get("indici_semantici", [])
        
        html_output += f"""
    <div class="section">
        <h2>{html.escape("testo completo unificato senza titoli")}</h2>
        <p class="subtitle">Matrice di origine con lettere evidenziate</p>
        
        {crea_matrice_html(testo, indici_saltatoria, indici_semantici)}
        
        <h3>ESTRAZIONE SALTATORIA (TIPO WEISSMANDEL)</h3>
        <div class="results-container">
        """
        
        if "saltatoria_ordinata" in risultati and risultati["saltatoria_ordinata"]:
            for parola in risultati["saltatoria_ordinata"]:
                html_output += f'<span class="result-word">{html.escape(parola)}</span>'
        else:
            html_output += '<p>Nessun risultato</p>'
        
        html_output += """
        </div>
        
        <h3>INCROCI SEMANTICI (TIPO DROSNIN)</h3>
        <div class="results-container">
        """
        
        if "semantici" in risultati and risultati["semantici"]:
            for risultato in risultati["semantici"]:
                html_output += f'<span class="result-semantic">{html.escape(risultato)}</span>'
        else:
            html_output += '<p>Nessun risultato</p>'
        
        html_output += """
        </div>
    </div>
        """
    
    html_output += """
</body>
</html>
    """
    
    return html_output

def main():
    """Funzione principale del programma"""
    if len(sys.argv) != 3:
        print("Utilizzo: python estrazione_semantica_pdf.py <percorso_file.pdf> num_salto")
        sys.exit(1)
    
    percorso_file = sys.argv[1]
    salto = sys.argv[2]
    #parse int 
    try:
        salto = int(salto)
    except ValueError:
        print("Errore: Il numero di salto deve essere un numero intero.")
        sys.exit(1)
    
    if salto <= 0:
        print("Errore: Il numero di salto deve essere maggiore di 0.")
        sys.exit(1)
    
    # Verifica se il file PDF esiste e se è in formato corretto
    # Utilizza PyMuPDF per leggere il file PDF e verificare il formato

    if not os.path.exists(percorso_file):
        print(f"Errore: Il file '{percorso_file}' non esiste.")
        sys.exit(1)
        
    if not percorso_file.endswith('.pdf'):
        print("Errore: Il file deve essere in formato PDF.")
        sys.exit(1)
    
    print(f"Analisi del file: {percorso_file}")
    print("Elaborazione in corso...\n")
    
    # Leggi il documento PDF
    paragrafi = leggi_pdf(percorso_file)
    
    # Dizionario per i risultati semplici (per output TXT)
    risultati = {}
    
    # Dizionario per i risultati estesi (per output HTML)
    risultati_estesi = {}
    
    testo_completo = " ".join(paragrafi.values())
    # testo tutto to lower
    testo_completo = testo_completo.lower()

    # Elabora ogni paragrafo
    #for titolo, testo in paragrafi.items():
        # Estrazione saltatoria con indici
    parole_saltatoria, indici_parole = estrazione_saltatoria(testo_completo, salto)
    
    # Ordina le parole saltatorie in base all'ordine di occorrenza nel testo
    # Crea una lista di tuple (parola, primo_indice) per l'ordinamento
    parole_con_indici = []
    for i, parola in enumerate(parole_saltatoria):
        if i < len(indici_parole) and indici_parole[i]:
            # Usa il primo indice di ogni parola per l'ordinamento
            primo_indice = min(indici_parole[i])
            parole_con_indici.append((parola, primo_indice))
    
    # Ordina le parole in base al primo indice (ordine di occorrenza nel testo)
    parole_con_indici.sort(key=lambda x: x[1])
    
    # Estrai solo le parole ordinate
    parole_saltatoria_ordinate = [parola for parola, _ in parole_con_indici]
        
    # Incroci semantici con dettagli
    risultati_semantici, dettagli_semantici = incroci_semantici(testo_completo, salto)
        
    # Raccogli tutti gli indici per evidenziazione HTML
    tutti_indici_saltatoria = []
    for indici_gruppo in indici_parole:
        tutti_indici_saltatoria.extend(indici_gruppo)
        
    tutti_indici_semantici = []
    for parola, occorrenze in dettagli_semantici.items():
        for salto, posizione, indici in occorrenze:
            tutti_indici_semantici.extend(indici)
        
    # Salva risultati semplici per output TXT
    risultati["testo completo unificato senza titoli"] = {
       "saltatoria": parole_saltatoria,
       "saltatoria_ordinata": parole_saltatoria_ordinate,
       "semantici": risultati_semantici
    }
        
    # Salva risultati estesi per output HTML
    risultati_estesi["testo completo unificato senza titoli"] = {
        "saltatoria": parole_saltatoria,
        "saltatoria_ordinata": parole_saltatoria_ordinate,
        "semantici": risultati_semantici,
        "indici_saltatoria": tutti_indici_saltatoria,
        "indici_semantici": tutti_indici_semantici,
        "dettagli_semantici": dettagli_semantici
    }    
    
    # Mostra i risultati in formato testo
    output_formattato = crea_output_formattato(risultati)
    print(output_formattato)
    
    # Salva i risultati in un file di testo
    nome_file_output_txt = os.path.splitext(percorso_file)[0] + "_risultati.txt"
    with open(nome_file_output_txt, 'w', encoding='utf-8') as f:
        f.write(output_formattato)
    
    # Genera e salva output HTML
    output_html = crea_output_html(paragrafi, risultati_estesi)
    nome_file_output_html = os.path.splitext(percorso_file)[0] + "_risultati.html"
    with open(nome_file_output_html, 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    print(f"\nI risultati sono stati salvati nei file:")
    print(f"- {nome_file_output_txt} (formato testo)")
    print(f"- {nome_file_output_html} (formato HTML con visualizzazione a matrice)")

if __name__ == "__main__":
    main()