# Poem4Astarte

Opensource poetry writing toolset and copilot

## Demo (italian only)
https://pegasus426.github.io/poem4astarte/index.html


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

