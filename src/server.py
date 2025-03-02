import spacy
from spacy_syllables import SpacySyllables
from transformers import AutoModelForCausalLM, AutoTokenizer

# Carica il modello italiano
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

def unisci_apostrofi(doc):
    """Unisce token che iniziano con un apostrofo al token precedente."""
    nuovi_token = []
    skip = False
    for i, token in enumerate(doc):
        if skip:
            skip = False
            continue
        # Se il token successivo inizia con apostrofo, unisci
        if i < len(doc) - 1 and token.text in ["l'", "d'", "s'"]:
            next_token = doc[i+1]
            unito = token.text + next_token.text
            nuovi_token.append(unito)
            skip = True
        else:
            nuovi_token.append(token.text)
    return nuovi_token




def conta_sinalefe_token(doc):
    """
    Conta le sinalefe iterando sui token:
    Se il token corrente termina per vocale ed il successivo inizia per vocale,
    si conta una sinalefa.
    Vengono ignorati i token che non hanno un conteggio di sillabe (punteggiatura, ecc.)
    """
    vowels = "aeiouàèéìòóù"
    count = 0
    for i in range(len(doc) - 1):
        token_curr = doc[i]
        token_next = doc[i+1]
        # Salta se uno dei due token non ha un conteggio
        if not token_curr._.syllables_count or not token_next._.syllables_count:
            continue
        # Rimuove eventuali apostrofi o punteggiatura dai bordi
        text_curr = token_curr.text.strip(" '’\".,;:!?").lower()
        text_next = token_next.text.strip(" '’\".,;:!?").lower()
        if text_curr and text_next:
            if text_curr[-1] in vowels and text_next[0] in vowels:
                count += 1
    return count

def conta_sillabe_corrette(verso):
    doc = verso
    # Somma delle sillabe per ogni token (saltando token che non hanno un conteggio)
    totale_sillabe = sum(token._.syllables_count for token in doc if token._.syllables_count)
    # Conta le sinalefe basandosi sui token
    num_sinalefe = conta_sinalefe_token(doc)
    totale_corretto = totale_sillabe - num_sinalefe

    # Gestione dei versi tronchi: se l'ultimo token (con sillabe) finisce con vocale accentata,
    # è probabile che il verso sia tronco, quindi si aggiunge 1 sillaba
    tokens_con_sillabe = [token for token in doc if token._.syllables_count]
    if tokens_con_sillabe:
        ultimo = tokens_con_sillabe[-1].text.strip(" '’\".,;:!?")
        if ultimo and ultimo[-1] in "àéíóú":
            totale_corretto += 1

    return totale_corretto, num_sinalefe, doc

# Analisi dei versi
for verso in poem.split("\n"):
    # Salta eventuali righe vuote
    if not verso.strip():
        continue
    verso_token_list = unisci_apostrofi(nlp(verso))  # lista di stringhe
    verso_unito = " ".join(verso_token_list)          # ricompone il testo
    doc = nlp(verso_unito)                            # tokenizza di nuovo
    totale_corretto, num_sinalefe, doc = conta_sillabe_corrette(doc)
    print("\nAnalisi per parola:")
    for token in doc:
        # Mostra solo i token con conteggio, per chiarezza
        if token._.syllables_count:
            print(f"{token.text:<15} {token._.syllables} ({token._.syllables_count} sillabe)")
        else:
            print(f"{token.text:<15} -")
    print(f"\nTotale sillabe nel verso (corretto per sinalefe e tronche): {totale_corretto}")
    print(f"Numero di sinalefe rilevate: {num_sinalefe}")
    print("È un endecasillabo?", totale_corretto == 11)

from pathlib import Path

# Percorso relativo alla directory del progetto
BASE_DIR = Path(__file__).resolve().parent

# Cartella per la cache Hugging Face dentro il progetto
CACHE_DIR = BASE_DIR / "cache"

# Carica modello e tokenizer usando il percorso relativo
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(CACHE_DIR))
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=str(CACHE_DIR))



prompt = "Mi rispondi sei pronto?"
input_ids = tokenizer(prompt, return_tensors="pt").input_ids

output = model.generate(input_ids, max_length=100, do_sample=True, top_p=0.95, top_k=50)
risposta = tokenizer.decode(output[0], skip_special_tokens=True)
print(risposta)
