import re
import spacy
from spacy_syllables import SpacySyllables

# Carica il modello italiano e il modulo per il conteggio delle sillabe
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

# Dizionario di eccezioni metriche
ECCEZIONI = {
    "mio": 2,         # "mio" scandito in due sillabe nella metrica poetica
    "tuo": 2,
    "suo": 2,
    "l'amor": 2,      # forma poetica di "l'amore"
    "d'amor": 2,
    "ch'in": 2,
    "un'amor": 2,
    "io": 2,          # forzato a 2 sillabe
    # Eccezioni per forme contratte unite:
    "l'primo": 3,     # "l'primo" da scandire come 3 sillabe (es. "l'-pri-mo")
    "ch'intrate": 3,  # "ch'intrate" scandito in 3 sillabe
}

def preprocess_text(text):
    """
    Pre-elabora il testo per unire le forme contratte.
    - Rimuove spazi superflui prima degli apostrofi (es. trasforma " 'l" in "l'")
    - Unisce tramite regex sequenze come "l' amore" in "l'amore" o "ch' intrate" in "ch'intrate".
    """
    # Rimuove spazi prima degli apostrofi: " 'l" → "l'"
    text = re.sub(r"\s+['’]", "'", text)
    # Unisce le forme contratte: ad esempio "l' amore" diventa "l'amore"
    text = re.sub(r"\b(l|d|s|ch)['’]\s+", r"\1'", text)
    return text

def conta_sillabe_token(token):
    """
    Restituisce il numero di sillabe per il token.
    Se il token è vuoto o è solo punteggiatura, restituisce 0.
    Se il token (pulito) è presente in ECCEZIONI, restituisce il valore definito.
    Altrimenti usa il conteggio della libreria.
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
    Si considera sinalefa se la fine di un token e l'inizio del successivo sono vocali.
    Ignora token che sono punteggiatura e gestisce il caso in cui il token successivo
    inizi con "h" muta.
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
      - Somma le sillabe di ogni token (con eccezioni)
      - Sottrae le sinalefe
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
