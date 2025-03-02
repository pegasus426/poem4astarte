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
