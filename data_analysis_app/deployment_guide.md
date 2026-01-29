# 🚀 Guida al Deployment su GitHub

Ho configurato Git sul tuo computer e ho preparato i file.
Ecco l'ultimo passaggio che devi fare tu (perché serve la tua password/account):

## 1. Crea il Repository
1. Vai su [github.com/new](https://github.com/new).
2. Nome Repository: `data-analysis-app` (o quello che preferisci).
3. **IMPORTANTE**: Lascia tutto il resto vuoto (Non aggiungere README, .gitignore o license).
4. Clicca **Create repository**.

## 2. Collega e Carica
Copia queste tre righe, incollale nel terminale e premi Invio:

```bash
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/data-analysis-app.git
git push -u origin main
```
*(Sostituisci `TUO_USERNAME` con il tuo vero nome utente GitHub)*

## 3. Pubblica su Streamlit
1. Vai su [share.streamlit.io](https://share.streamlit.io).
2. Clicca **New App**.
3. Seleziona `data-analysis-app`.
4. Clicca **Deploy**.
