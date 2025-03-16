#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import docx
import sys
import re
import os
from typing import List, Dict, Tuple
import html

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

def estrazione_saltatoria(testo: str, salto: int = 50) -> Tuple[List[str], List[int]]:
    """
    Esegue un'estrazione saltatoria con il passo specificato (tipo Weissmandel).
    
    Args:
        testo: Il testo da cui estrarre
        salto: Il numero di caratteri da saltare tra un'estrazione e l'altra
        
    Returns:
        Tupla con lista di parole estratte e lista di indici dei caratteri nel testo originale
    """
    # Rimuovi spazi e normalizza il testo
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    
    risultato = []
    caratteri_estratti = []
    indici_estratti = []
    
    # Se il testo è troppo corto per applicare il salto
    if len(testo_pulito) < salto:
        return ["Testo troppo corto per estrazione saltatoria"], []
    
    for indice in range(0, len(testo_pulito), salto):
        if indice < len(testo_pulito):
            caratteri_estratti.append(testo_pulito[indice])
            indici_estratti.append(indice)
    
    # Raggruppa in gruppi di 3 caratteri per formare "parole"
    parole = []
    indici_parole = []
    for i in range(0, len(caratteri_estratti), 3):
        gruppo = caratteri_estratti[i:i+3]
        indici_gruppo = indici_estratti[i:i+3]
        if len(gruppo) == 3:  # Prendi solo gruppi completi di 3
            parole.append(''.join(gruppo))
            indici_parole.append(indici_gruppo)
    
    return parole, indici_parole

def incroci_semantici(testo: str) -> Tuple[List[str], Dict[str, List[Tuple[int, int, int]]]]:
    """
    Identifica incroci semantici nel testo (tipo Michael Drosnin).
    
    Args:
        testo: Il testo da analizzare
        
    Returns:
        Tupla con lista di risultati e dizionario con dettagli delle occorrenze
    """
    # Lista di parole significative da cercare (esempio)
    parole_chiave = ["dio", "vita", "morte", "amore", "pace", "guerra", 
                     "luce", "buio", "bene", "male", "verità", "fede"]
    
    testo_pulito = re.sub(r'\s+', '', testo).lower()
    risultati = []
    dettagli_occorrenze = {}
    
    # Cerca sequenze ELS per ogni parola chiave
    for parola in parole_chiave:
        for salto in range(2, 50):  # Prova diversi salti
            for posizione_iniziale in range(salto):
                sequenza = ""
                indici = []
                for i in range(posizione_iniziale, len(testo_pulito), salto):
                    sequenza += testo_pulito[i]
                    indici.append(i)
                
                if parola in sequenza:
                    risultati.append(f"{parola} (salto: {salto})")
                    
                    # Trova l'indice di inizio della parola nella sequenza
                    indice_inizio_seq = sequenza.find(parola)
                    # Calcola gli indici corrispondenti nel testo originale
                    indici_parola = indici[indice_inizio_seq:indice_inizio_seq+len(parola)]
                    
                    # Memorizza i dettagli di questa occorrenza
                    if parola not in dettagli_occorrenze:
                        dettagli_occorrenze[parola] = []
                    
                    dettagli_occorrenze[parola].append((salto, posizione_iniziale, indici_parola))
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
            background-color: #f8f9fa;
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
        .matrix {
            font-family: monospace;
            line-height: 1.5;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #f1f3f5;
            padding: 15px;
            border-radius: 4px;
            position: relative;
        }
        .highlight {
            background-color: #ffeb3b;
            color: #000;
            font-weight: bold;
            padding: 2px;
            border-radius: 3px;
        }
        .matrix span.saltatory {
            background-color: #4caf50;
            color: white;
            padding: 2px;
            border-radius: 3px;
        }
        .matrix span.semantic {
            background-color: #2196f3;
            color: white;
            padding: 2px;
            border-radius: 3px;
        }
        .result-item {
            background-color: #e8f5e9;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .result-word {
            font-weight: bold;
            color: #1b5e20;
        }
        .result-semantic {
            background-color: #e3f2fd;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .result-semantic .result-word {
            color: #0d47a1;
        }
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
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
            background-color: #4caf50;
        }
        .blue {
            background-color: #2196f3;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .grid-item {
            font-family: monospace;
            padding: 8px;
            text-align: center;
            border-radius: 3px;
            background-color: #f1f3f5;
        }
    </style>
</head>
<body>
    <header>
        <h1>Estrazione Semantica - Risultati</h1>
    </header>
    """
    
    for titolo, testo in paragrafi.items():
        # Pulisci il testo per visualizzazione HTML
        testo_pulito = re.sub(r'\s+', '', testo).lower()
        risultati = risultati_estesi.get(titolo, {})
        
        html_output += f"""
    <div class="section">
        <h2>{html.escape(titolo)}</h2>
        
        <h3>Matrice di Origine</h3>
        <div class="matrix" id="matrix-{hash(titolo)}">
        """
        
        # Crea una rappresentazione HTML del testo con caratteri evidenziati
        testo_html = ""
        for i, carattere in enumerate(testo_pulito):
            char_class = ""
            if "indici_saltatoria" in risultati and i in risultati["indici_saltatoria"]:
                char_class = "saltatory"
            elif "indici_semantici" in risultati and i in risultati["indici_semantici"]:
                char_class = "semantic"
            
            if char_class:
                testo_html += f'<span class="{char_class}">{html.escape(carattere)}</span>'
            else:
                testo_html += html.escape(carattere)
        
        html_output += testo_html
        html_output += """
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color green"></div>
                <span>Estrazione Saltatoria</span>
            </div>
            <div class="legend-item">
                <div class="legend-color blue"></div>
                <span>Incroci Semantici</span>
            </div>
        </div>
        """
        
        # Aggiungi sezione per estrazione saltatoria
        html_output += """
        <h3>ESTRAZIONE SALTATORIA (TIPO WEISSMANDEL)</h3>
        """
        
        if "saltatoria" in risultati and risultati["saltatoria"]:
            html_output += '<div class="grid-container">'
            for parola in risultati["saltatoria"]:
                html_output += f'<div class="grid-item result-word">{html.escape(parola)}</div>'
            html_output += '</div>'
        else:
            html_output += '<p>Nessun risultato</p>'
        
        # Aggiungi sezione per incroci semantici
        html_output += """
        <h3>INCROCI SEMANTICI (TIPO DROSNIN)</h3>
        """
        
        if "semantici" in risultati and risultati["semantici"]:
            for i, risultato in enumerate(risultati["semantici"]):
                html_output += f'<div class="result-semantic"><span class="result-word">{html.escape(risultato)}</span></div>'
        else:
            html_output += '<p>Nessun risultato</p>'
        
        html_output += """
    </div>
        """
    
    html_output += """
</body>
</html>
    """
    
    return html_output

def main():
    """Funzione principale del programma"""
    if len(sys.argv) != 2:
        print("Utilizzo: python estrazione_semantica.py <percorso_file.docx>")
        sys.exit(1)
    
    percorso_file = sys.argv[1]
    
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
    
    # Dizionario per i risultati semplici (per output TXT)
    risultati = {}
    
    # Dizionario per i risultati estesi (per output HTML)
    risultati_estesi = {}
    
    # Elabora ogni paragrafo
    for titolo, testo in paragrafi.items():
        # Estrazione saltatoria con indici
        parole_saltatoria, indici_parole = estrazione_saltatoria(testo)
        
        # Incroci semantici con dettagli
        risultati_semantici, dettagli_semantici = incroci_semantici(testo)
        
        # Raccogli tutti gli indici per evidenziazione HTML
        tutti_indici_saltatoria = []
        for indici_gruppo in indici_parole:
            tutti_indici_saltatoria.extend(indici_gruppo)
        
        tutti_indici_semantici = []
        for parola, occorrenze in dettagli_semantici.items():
            for salto, posizione, indici in occorrenze:
                tutti_indici_semantici.extend(indici)
        
        # Salva risultati semplici per output TXT
        risultati[titolo] = {
            "saltatoria": parole_saltatoria,
            "semantici": risultati_semantici
        }
        
        # Salva risultati estesi per output HTML
        risultati_estesi[titolo] = {
            "saltatoria": parole_saltatoria,
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
    print(f"- {nome_file_output_html} (formato HTML con visualizzazione grafica)")

if __name__ == "__main__":
    main()
