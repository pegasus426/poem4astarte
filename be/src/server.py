import re
import sqlite3
import spacy
from spacy_syllables import SpacySyllables

# --- Configurazione SQLite per le eccezioni metriche ---
DB_PATH = "eccezioni_metriche.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Crea la tabella se non esiste
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eccezioni (
            parola TEXT PRIMARY KEY,
            sillabe INTEGER
        )
    """)
    # Inserisce le eccezioni iniziali se non già presenti
    eccezioni_iniziali = {
        "mio": 2,
        "tuo": 2,
        "suo": 2,
        "l'amor": 2,
        "d'amor": 2,
        "ch'in": 2,
        "un'amor": 2,
        "io": 2,
        "l'primo": 3,
        "ch'intrate": 3,
    }
    for parola, sillabe in eccezioni_iniziali.items():
        # Usa INSERT OR IGNORE per non sovrascrivere eventuali valori già presenti
        cur.execute("INSERT OR IGNORE INTO eccezioni (parola, sillabe) VALUES (?, ?)", (parola, sillabe))
    conn.commit()
    conn.close()

def load_eccezioni():
    """Recupera le eccezioni dal database e le restituisce in un dizionario."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT parola, sillabe FROM eccezioni")
    rows = cur.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

# Inizializza il DB e carica le eccezioni
init_db()
ECCEZIONI = load_eccezioni()

# --- Caricamento modello spaCy e modulo sillabe ---
nlp = spacy.load("it_core_news_sm")
syllables = SpacySyllables(nlp)
nlp.add_pipe("syllables", after="tagger")

# Testo da analizzare (Dante)
poem = """Per me si va ne la città dolente,
per me si va ne l'etterno dolore,
per me si va tra la perduta gente.

Giustizia mosse il mio alto fattore;
fecemi la divina potestate
la somma sapïenza e 'l primo amore.

Dinanzi a me non fuor cose create
se non etterne, e io etterno duro.
Lasciate ogne speranza, voi ch'intrate."""

def preprocess_text(text):
    """
    Pre-elabora il testo per unire le forme contratte.
    Rimuove spazi prima degli apostrofi e unisce sequenze come "l' amore" in "l'amore".
    """
    text = re.sub(r"\s+['’]", "'", text)
    text = re.sub(r"\b(l|d|s|ch)['’]\s+", r"\1'", text)
    return text

def conta_sillabe_token(token):
    ECCEZIONI = load_eccezioni()
    """
    Restituisce il numero di sillabe per il token.
    Se il token è vuoto o è solo punteggiatura, restituisce 0.
    Se il token (pulito) è presente in ECCEZIONI, restituisce il valore definito.
    Altrimenti, usa il conteggio della libreria.
    """
    token_text = token.text.strip(" '’\".,;:!?").lower()
    if not token_text:
        return 0
    if token_text in ECCEZIONI:
        return ECCEZIONI[token_text]
    return token._.syllables_count if token._.syllables_count else 0

def conta_sinalefe_token(doc):
    """
    Conta le sinalefe nel documento (lista di token).
    Una sinalefa si verifica se la fine di un token e l'inizio del successivo sono vocali.
    Ignora token di punteggiatura e gestisce il caso in cui il token successivo inizi con "h" muta.
    """
    vowels = "aeiouàèéìòóù"
    count = 0
    for i in range(len(doc) - 1):
        t_curr = doc[i].text.strip(" '’\".,;:!?").lower()
        t_next = doc[i+1].text.strip(" '’\".,;:!?").lower()
        if not t_curr or not t_next:
            continue
        if doc[i+1].text in [",", ";", ".", ":", "!", "?"]:
            continue
        if t_next.startswith("h") and len(t_next) > 1 and t_next[1] in vowels:
            t_next = t_next[1:]
        if t_curr[-1] in vowels and t_next[0] in vowels:
            count += 1
    return count

def conta_sillabe_corrette(doc):
    """
    Calcola il totale delle sillabe in un verso:
      - Somma le sillabe di ogni token (utilizzando le eccezioni)
      - Sottrae il numero di sinalefe
      - Se l'ultimo token utile termina con vocale accentata (verso tronco), aggiunge 1 sillaba.
    """
    totale_sillabe = sum(conta_sillabe_token(token) for token in doc)
    num_sinalefe = conta_sinalefe_token(doc)
    totale_corretto = totale_sillabe - num_sinalefe

    tokens_utili = [token for token in doc if conta_sillabe_token(token) > 0]
    if tokens_utili:
        ultimo = tokens_utili[-1].text.strip(" '’\".,;:!?")
        if ultimo and ultimo[-1] in "àéíóú":
            totale_corretto += 1
    return totale_corretto, num_sinalefe, doc

# Elaborazione verso per verso
for verso in poem.split("\n"):
    if not verso.strip():
        continue
    # Pre-elabora il verso per unire le forme contratte
    verso_pre = preprocess_text(verso)
    doc = nlp(verso_pre)
    totale_corretto, num_sinalefe, doc = conta_sillabe_corrette(doc)
    print("\nAnalisi per parola:")
    for token in doc:
        count = conta_sillabe_token(token)
        if count:
            print(f"{token.text:<15} {token._.syllables} ({count} sillabe)")
        else:
            print(f"{token.text:<15} -")
    print(f"\nTotale sillabe nel verso (corretto per sinalefe e tronche): {totale_corretto}")
    print(f"Numero di sinalefe rilevate: {num_sinalefe}")
    print("È un endecasillabo?", totale_corretto == 11)
