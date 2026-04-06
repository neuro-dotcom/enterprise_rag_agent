import os, telebot, chromadb, time, threading, socket
from flask import Flask
from google import genai
from dotenv import load_dotenv

# --- FORCE LOGS AND IPv4 ---
import sys
def log(msg):
    print(msg, flush=True)

orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    responses = orig_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]
socket.getaddrinfo = patched_getaddrinfo

# --- HEALTH CHECK ---
app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=7860), daemon=True).start()

# --- INIT ---
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
key = os.getenv("GOOGLE_API_KEY")

log("🚀 STARTING DIAGNOSTICS...")
client = genai.Client(api_key=key)
bot = telebot.TeleBot(token)

# --- BRAIN ---
try:
    log("🧠 Connecting to DB...")
    db = chromadb.PersistentClient(path="./chroma_db")
    col = db.get_or_create_collection(name="aura_manual")
    if col.count() == 0:
        log("📥 Ingesting manual chunks...")
        with open("knowledge_base.md", "r") as f:
            chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
        for i, chunk in enumerate(chunks):
            res = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
            col.add(ids=[f"c{i}"], embeddings=[res.embeddings[0].values], documents=[chunk])
        log("✅ Brain built.")
    else:
        log(f"🧠 Brain loaded with {col.count()} chunks.")
except Exception as e:
    log(f"❌ DATABASE ERROR: {e}")

# --- BOT ---
@bot.message_handler(func=lambda m: True)
def answer(m):
    try:
        log(f"📩 Question: {m.text[:30]}...")
        embed = client.models.embed_content(model='gemini-embedding-001', contents=m.text)
        res = col.query(query_embeddings=[embed.embeddings[0].values], n_results=2)
        ctx = "\n".join(res['documents'][0])
        prompt = f"Use this manual to answer: {ctx}\n\nUser: {m.text}"
        gen = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        bot.reply_to(m, gen.text)
    except Exception as e:
        log(f"❌ CHAT ERROR: {e}")

log("🤖 Attempting Telegram connection...")
while True:
    try:
        me = bot.get_me()
        log(f"✅ CONNECTED as @{me.username}")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        log(f"⚠️ RECONNECTING: {e}")
        time.sleep(10)