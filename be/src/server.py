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
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# Percorso del modello su Hugging Face
model_name = "jan-hq/stealth-v1.2"

# Caricamento del tokenizer e del modello con cache_dir
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=CACHE_DIR)
# Imposta manualmente il pad_token_id per evitare warning
tokenizer.pad_token = tokenizer.eos_token

# Conversazione iniziale
conversation = [
    {"role": "system", "content": "Sei la Dea Astarte Syriaca, una divinità antica e saggia. Rispondi sempre nel ruolo della Dea."},
    {"role": "system", "content": "Stai girando in un software realizzao da Stefano (user) per l'analii della metrica poetica durante la scritura poetica"},
    {"role": "user", "content": "Sono Stefano un'aspirante poeta di origine Italiana"},
    {"role": "user", "content": "La poesia che ho scrito è la seguente:"},
    {"role": "user", "content": poem},
    {"role": "user", "content": "Vorrei sapere se sei felice di questa poesia? o se è un affanno ridicolo lavorarci? Voglio sapere inoltre se segue una metrica"}
]

# Funzione per formattare la conversazione con delimitatori specifici
def format_conversation(conversation):
    formatted_text = ""
    for message in conversation:
        if message["role"] == "system":
            formatted_text += f"<|im_start|>system\n{message['content']}<|im_end|>\n"
        elif message["role"] == "user":
            formatted_text += f"<|im_start|>user\n{message['content']}<|im_end|>\n"
        elif message["role"] == "assistant":
            formatted_text += f"<|im_start|>assistant\n{message['content']}<|im_end|>\n"
    return formatted_text.strip()

# Formatta la conversazione e aggiungi il prompt dell'assistente
prompt = format_conversation(conversation) + "\n<|im_start|>assistant\n"

# Tokenizzazione con padding e attention_mask
inputs = tokenizer(prompt, return_tensors="pt", padding=True)

# Generazione della risposta
outputs = model.generate(
    inputs.input_ids,
    attention_mask=inputs.attention_mask,  # Evita problemi con il padding
    max_length=8192,  # Lunghezza massima della risposta
    do_sample=True,  # Attiva la generazione casuale
    top_p=0.95,  # Nucleus sampling: tiene il top 95% della probabilità cumulativa
    top_k=50,  # Considera solo i 50 token più probabili
    temperature=0.7,  # Controlla la casualità (più basso = più deterministico)
    repetition_penalty=1.1,  # Penalizza ripetizioni per migliorare la diversità
    num_return_sequences=1,  # Numero di risposte generate
    early_stopping=True,  # Termina la generazione quando viene raggiunto un token di stop
    pad_token_id=tokenizer.pad_token_id,  # Evita warning sui token di padding
    eos_token_id=tokenizer.eos_token_id,  # Token di fine sequenza
    length_penalty=1.0,  # Penalizza sequenze troppo lunghe o corte (1.0 = neutro)
    num_beams=1, # Usa beam search con 2 percorsi esplorati
) 


# Decodifica della risposta
risposta = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Rimuove il testo prima dell'assistente per estrarre solo la risposta
risposta = risposta.split("<|im_start|>assistant\n")[-1].strip()
risposta = risposta.split("<|im_end|>")[0].strip()  # Rimuove eventuali delimitatori residui

# Aggiunta della risposta alla conversazione
conversation.append({"role": "assistant", "content": risposta})

# Stampa della risposta
print(risposta)
