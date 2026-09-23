# Physics Lab AI
Domain-specific Flask + Gemini chatbot.

## Local
`pip install -r requirements.txt`
Copy `.env.example` to `.env`, add your Gemini API key, then run `python app.py`.
Open `http://localhost:10000`.

## Render
Build: `pip install -r requirements.txt`
Start: `gunicorn app:app`
Add `GEMINI_API_KEY` and `FLASK_SECRET_KEY` in Render Environment Variables. Render provides `PORT`.

## Configuration
Edit `config.py` for title, domain, system prompt, welcome message, theme and UI settings.
