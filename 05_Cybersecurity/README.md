# Cyber Shield Academy

Flask + Gemini 3.1 Flash-Lite domain-specific study chatbot.

## Local
1. `pip install -r requirements.txt`
2. Put your real `GEMINI_API_KEY` and strong `FLASK_SECRET_KEY` in `.env`.
3. Run `python app.py` and open `http://127.0.0.1:5000`.

## Render
Build: `pip install -r requirements.txt`
Start: `gunicorn app:app`
Add `GEMINI_API_KEY` and `FLASK_SECRET_KEY` as Render environment variables. Render supplies `PORT` and the app reads it automatically.

No login/register is included. Temporary history is kept in the signed Flask session cookie, so there is no shared server-side conversation store. API keys are server-only. The API also uses a per-session CSRF token and bounded input/history.
