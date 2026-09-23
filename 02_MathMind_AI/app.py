import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google import genai
from google.genai import types
import config
load_dotenv()
app=Flask(__name__)
app.secret_key=config.SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",SESSION_COOKIE_SECURE=config.SESSION_COOKIE_SECURE)
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None
def hist(): return session.setdefault("chat_history",[])
@app.get("/")
def index(): return render_template("index.html",title=config.CHATBOT_TITLE,domain=config.DOMAIN,welcome=config.WELCOME_MESSAGE,theme=config.THEME)
@app.get("/health")
def health(): return jsonify(status="ok",model=config.MODEL)
@app.post("/api/chat")
def chat():
    data=request.get_json(silent=True) or {}; msg=str(data.get("message","")).strip()
    if not msg: return jsonify(error="Please enter a message."),400
    if len(msg)>config.MAX_MESSAGE_CHARS: return jsonify(error="Message is too long."),400
    if client is None: return jsonify(error="Gemini API key is not configured on the server."),503
    contents=[types.Content(role=x["role"],parts=[types.Part.from_text(text=x["text"])]) for x in hist()[-config.MAX_HISTORY:]]
    contents.append(types.Content(role="user",parts=[types.Part.from_text(text=msg)]))
    try:
        r=client.models.generate_content(model=config.MODEL,contents=contents,config=types.GenerateContentConfig(system_instruction=config.SYSTEM_PROMPT,temperature=.3,max_output_tokens=900))
        answer=(r.text or "").strip() or "I couldn't generate a response. Please try again."
        hist().extend([{"role":"user","text":msg},{"role":"model","text":answer}]); session.modified=True
        return jsonify(answer=answer)
    except Exception:
        return jsonify(error="The AI service is temporarily unavailable. Please try again."),502
@app.post("/api/clear")
def clear(): session["chat_history"]=[]; session.modified=True; return jsonify(ok=True)
if __name__=="__main__": app.run(host="0.0.0.0",port=config.PORT)
