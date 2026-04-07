import os, telebot, chromadb, time, threading, socket
from flask import Flask
from google import genai
from dotenv import load_dotenv

# ==========================================
# 🛑 THE "ZERO-DOUBT" DNS BYPASS
# ==========================================
# Hugging Face 2026 DNS is currently failing to resolve Telegram.
# We are hardcoding the IP (149.154.167.220) directly.
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == 'api.telegram.org':
        # Force the connection to the physical IP address of Telegram
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('149.154.167.220', 443))]
    return orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = patched_getaddrinfo

# --- LOGGING ---
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# --- HEALTH CHECK (Satisfies Hugging Face Policy) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Aura Bot is Online", 200
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=7860), daemon=True).start()

# --- INITIALIZATION ---
load_dotenv()
log("🚀 STARTING AURA SUPPORT AGENT...")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# --- BRAIN BUILDING (Runtime) ---
db = chromadb.PersistentClient(path="./chroma_db")
col = db.get_or_create_collection(name="aura_manual")

if col.count() == 0:
    log("🧠 Brain is empty. Ingesting manual...")
    with open("knowledge_base.md", "r", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
    for i, chunk in enumerate(chunks):
        res = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
        col.add(ids=[f"c{i}"], embeddings=[res.embeddings[0].values], documents=[chunk])
    log(f"✅ Brain built with {len(chunks)} chunks.")

# --- RAG HANDLER ---
@bot.message_handler(func=lambda m: True)
def handle_query(m):
    try:
        log(f"📩 Query received: {m.text[:30]}...")
        embed = client.models.embed_content(model='gemini-embedding-001', contents=m.text)
        res = col.query(query_embeddings=[embed.embeddings[0].values], n_results=2)
        context = "\n\n".join(res['documents'][0])
        
        prompt = f"You are a Support AI. Use this manual: {context}\n\nUser Question: {m.text}"
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        bot.reply_to(m, response.text)
    except Exception as e:
        log(f"❌ CHAT ERROR: {e}")

# --- INFINITY POLLING ---
log("🤖 Attempting Telegram connection via Hardcoded IP...")
while True:
    try:
        # We skip bot.get_me() to save a request and go straight to listening
        bot.infinity_polling(timeout=90, long_polling_timeout=30)
    except Exception as e:
        log(f"⚠️ RECONNECTING: {e}")
        time.sleep(10)