import os, telebot, chromadb, time, threading, socket, json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from google import genai
from dotenv import load_dotenv

# --- HARDCODED IP BYPASS ---
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == 'api.telegram.org':
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('149.154.167.220', 443))]
    return orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = patched_getaddrinfo

def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# --- HEALTH CHECK ---
app = Flask(__name__)
@app.route('/')
def health(): return "Aura Bot is Online", 200
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=7860), daemon=True).start()

# --- INITIALIZATION ---
load_dotenv()
log("🚀 STARTING AURA SUPPORT AGENT...")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))
GUESTS_FILE = "guests.json"

# --- DATABASE HELPERS ---
def load_guests():
    if os.path.exists(GUESTS_FILE):
        with open(GUESTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_guests(guests):
    with open(GUESTS_FILE, "w") as f:
        json.dump(guests, f)

# --- BRAIN BUILDING ---
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

# ==========================================
# 🛡️ ADMIN DASHBOARD & GUEST MANAGEMENT
# ==========================================
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.chat.id != ADMIN_CHAT_ID:
        return # Silently ignore unauthorized users
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Add Guest (2 Requests)", callback_data="add_guest"))
    bot.reply_to(m, "🛡️ **Admin Dashboard**\nManage bot access below:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "add_guest")
def add_guest_callback(call):
    if call.message.chat.id != ADMIN_CHAT_ID: return
    
    msg = bot.send_message(call.message.chat.id, "Please enter the numeric Telegram Chat ID of the recruiter/tester:")
    bot.register_next_step_handler(msg, process_guest_id)

def process_guest_id(m):
    try:
        guest_id = str(int(m.text.strip())) # Validate it's a number
        guests = load_guests()
        guests[guest_id] = 2 # Grant exact quota
        save_guests(guests)
        bot.reply_to(m, f"✅ Guest Access Granted.\nID: `{guest_id}`\nQuota: 2 requests.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(m, "❌ Invalid ID. Please enter numbers only. Try /admin again.")

# ==========================================
# 🧠 RAG HANDLER WITH SMART BOUNCER
# ==========================================
@bot.message_handler(func=lambda m: True)
def handle_query(m):
    user_id = str(m.chat.id)
    is_admin = (m.chat.id == ADMIN_CHAT_ID)
    
    guests = load_guests()
    is_guest = user_id in guests

    # 1. Access Control Logic
    if not is_admin:
        if not is_guest:
            log(f"⚠️ UNAUTHORIZED ACCESS ATTEMPT FROM ID: {user_id}")
            bot.reply_to(m, "⛔ Access Denied: Enterprise system restricted.")
            return
        
        if guests[user_id] <= 0:
            bot.reply_to(m, "🛑 Demo complete. Thank you for testing the RAG Support Agent architecture.")
            return

    # 2. Process Query
    try:
        log(f"📩 Query from {user_id}: {m.text[:30]}...")
        embed = client.models.embed_content(model='gemini-embedding-001', contents=m.text)
        res = col.query(query_embeddings=[embed.embeddings[0].values], n_results=2)
        context = "\n\n".join(res['documents'][0])
        
        prompt = f"You are a Support AI. Use this manual: {context}\n\nUser Question: {m.text}"
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        
        # 3. Handle Quota Subtraction & Messaging
        if is_guest:
            guests[user_id] -= 1
            save_guests(guests)
            footer = f"\n\n_*(Guest Quota Remaining: {guests[user_id]})*_"
            bot.reply_to(m, response.text + footer, parse_mode="Markdown")
        else:
            bot.reply_to(m, response.text)

    except Exception as e:
        log(f"❌ CHAT ERROR: {e}")

# --- INFINITY POLLING ---
log("🤖 Attempting Telegram connection via Hardcoded IP...")
while True:
    try:
        bot.infinity_polling(timeout=90, long_polling_timeout=30)
    except Exception as e:
        log(f"⚠️ RECONNECTING: {e}")
        time.sleep(10)