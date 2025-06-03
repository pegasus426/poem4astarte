# Poem4Astarte

Opensource poetry writing toolset and copilot

## Demo (italian only)

https://pegasus426.github.io/poem4astarte/index.html

https://tinyurl.com/syriatiamo


## Suported laguages
This tool is in initial development for now only italian is available

## Supported copilots
This tool is in initial development for now only jan-hq/stealth-v.1.2 is available

## Backend 
cd be
### frist time italian
poetry run python -m spacy download it_core_news_sm

poetry run python src/server.py
poetry run uvicorn src.main:app --reload

## Frontend
cd fe
open in browser index.html

## Estrazioni semantiche
```
poetry add docx
poetry install
poetry shell
cd be
python3 src/estrazione-semantica.py ../../Il\ Mare\ Nero\ dell\'Ein-Sof\ \(v3\).docx 
ll ../../python3 src/estrazione-semantica.py ../../Il\ Mare\ Nero\ dell\'Ein-Sof\ \(v3\).docx 


## Chat server

# Inizializza il progetto Poetry (se non già fatto)
poetry init

# Aggiungi le dipendenze principali
poetry add transformers torch torchvision torchaudio

# Per GPU support (CUDA) - opzionale, installa solo se hai GPU NVIDIA
poetry add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Dipendenze aggiuntive per funzionalità avanzate
poetry add accelerate  # Per ottimizzazioni di caricamento modelli
poetry add safetensors  # Per formato di salvataggio sicuro dei modelli
poetry add huggingface-hub  # Per download modelli da Hugging Face

# Dipendenze per sviluppo (opzionali)
poetry add --group dev pytest black flake8 mypy

# Installa tutte le dipendenze
poetry install

# Attiva l'ambiente virtuale
poetry shell

# Oppure esegui direttamente l'applicazione
poetry run python chat_app.py


# Su Ubuntu/Debian - installa tkinter per Python 3.12
sudo apt update
sudo apt install python3.12-tk

# Oppure più generico (dovrebbe funzionare)
sudo apt install python3-tk

# Su altre distribuzioni:

# Fedora/RHEL/CentOS
sudo dnf install tkinter
# oppure
sudo yum install tkinter

# Arch Linux
sudo pacman -S tk

# Verifica che tkinter sia disponibile
python3 -c "import tkinter; print('Tkinter funziona!')"

# Se continua a non funzionare, prova a reinstallare Python con tkinter
sudo apt install python3.12-dev python3.12-tk python3.12-venv

# Oppure usando pyenv (se lo hai installato)
pyenv install 3.12.0
pyenv global 3.12.0