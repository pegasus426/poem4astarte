# Poem4Astarte

Opensource poetry writing toolset and copilot

## Suported laguages
This tool is in initial development for now only italian is available

## Backend 
cd be
### frist time italian
poetry run python -m spacy download it_core_news_sm

poetry run python src/server.py
poetry run uvicorn src.main:app --reload

## Frontend
cd fe

