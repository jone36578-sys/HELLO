import os,secrets,logging
from datetime import timedelta
from flask import Flask,jsonify,render_template,request,session
from flask_session import Session
from config import *
from google import genai
from google.genai import types
logging.basicConfig(level=logging.INFO)
app=Flask(__name__)
SESSION_DIR=os.path.join(os.getenv("TMPDIR", "/tmp"), "domain_chatbot_sessions")
os.makedirs(SESSION_DIR, exist_ok=True)
app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),SESSION_TYPE="filesystem",SESSION_FILE_DIR=SESSION_DIR,SESSION_PERMANENT=True,SESSION_USE_SIGNER=True,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",SESSION_COOKIE_SECURE=os.getenv("RENDER", "").lower()=="true",PERMANENT_SESSION_LIFETIME=timedelta(minutes=SESSION_TIMEOUT_MINUTES),MAX_CONTENT_LENGTH=32*1024)
Session(app)
def ensure():
    if "sid" not in session: session["sid"]=secrets.token_urlsafe(24)
    if "history" not in session: session["history"]=[]
    session.permanent=True
def in_scope(t): return any(x in t.lower() for x in DOMAIN_KEYWORDS)
def reject(): return f"I’m focused only on {DOMAIN}. Please ask a question related to that subject."
@app.get("/")
def index():
    ensure(); csrf=session.setdefault("csrf",secrets.token_urlsafe(24)); return render_template("index.html",config={"TITLE":TITLE,"DOMAIN":DOMAIN,"SHORT_LABEL":SHORT_LABEL,"WELCOME":WELCOME_MESSAGE,"MAX_INPUT_CHARS":MAX_INPUT_CHARS},csrf=csrf)
@app.get("/health")
def health(): return jsonify(status="ok",model=MODEL,domain=DOMAIN)
@app.post("/api/chat")
def chat():
    ensure(); p=request.get_json(silent=True) or {}
    if p.get("csrf")!=session.get("csrf"): return jsonify(error="Invalid session token. Refresh the page."),403
    msg=str(p.get("message","")).strip()
    if not msg:return jsonify(error="Please enter a question."),400
    if len(msg)>MAX_INPUT_CHARS:return jsonify(error=f"Please keep your message under {MAX_INPUT_CHARS} characters."),400
    h=session.get("history",[])
    if not in_scope(msg):
        r=reject(); h += [{"role":"user","text":msg},{"role":"model","text":r}]; session["history"]=h[-MAX_HISTORY_MESSAGES:]; session.modified=True; return jsonify(reply=r,history=session["history"])
    key=os.getenv("GEMINI_API_KEY")
    if not key:return jsonify(error="GEMINI_API_KEY is not configured on the server."),503
    try:
        client=genai.Client(api_key=key); contents="\n".join(f'{x["role"].upper()}: {x["text"]}' for x in h[-MAX_HISTORY_MESSAGES:]+[{"role":"user","text":msg}])
        resp=client.models.generate_content(model=MODEL,contents=contents,config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT,max_output_tokens=1200))
        r=(resp.text or "").strip()
        if not r: raise RuntimeError("Empty Gemini response")
    except Exception:
        logging.exception("Gemini request failed"); return jsonify(error="The AI service could not complete that request. Please try again."),502
    h += [{"role":"user","text":msg},{"role":"model","text":r}]; session["history"]=h[-MAX_HISTORY_MESSAGES:]; session.modified=True; return jsonify(reply=r,history=session["history"])
@app.post("/api/clear")
def clear():
    ensure(); p=request.get_json(silent=True) or {}
    if p.get("csrf")!=session.get("csrf"): return jsonify(error="Invalid session token."),403
    session["history"]=[]; session.modified=True; return jsonify(ok=True)
if __name__=="__main__": app.run(host="0.0.0.0",port=PORT,debug=False)
