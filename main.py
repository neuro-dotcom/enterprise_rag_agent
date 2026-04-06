import os
import telebot
import chromadb
import time
import socket
from google import genai
from dotenv import load_dotenv

# ==========================================
# 🌐 THE ENTERPRISE NETWORK FIX (Force IPv4)
# ==========================================
# Hugging Face 2026 Docker spaces have IPv6 DNS issues with Telegram.
# This forces the system to use IPv4 only.
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    responses = orig_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]
socket.getaddrinfo = patched_getaddrinfo
# ==========================================

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Clients
client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def build_knowledge_base():
    """Builds the brain if it doesn't exist."""
    if not os.path.exists("./chroma_db"):
        print("🧠 Building the Brain for the first time...")
        db = chromadb.PersistentClient(path="./chroma_db")
        collection = db.get_or_create_collection(name="aura_manual")
        
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
        
        for i, chunk in enumerate(chunks):
            response = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
            collection.add(ids=[f"c{i}"], embeddings=[response.embeddings[0].values], documents=[chunk])
        print("✅ Brain built successfully.")
    else:
        print("🧠 Brain already exists. Loading...")

# Connect to Database
build_knowledge_base()
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_collection(name="aura_manual")

@bot.message_handler(func=lambda message: True)
def handle_support_query(message):
    try:
        user_query = message.text
        embed_res = client.models.embed_content(model='gemini-embedding-001', contents=user_query)
        results = collection.query(query_embeddings=[embed_res.embeddings[0].values], n_results=2)
        
        system_prompt = f"""
        You are an Aura Smart Home AI support agent. 
        Use the manual to answer: {results['documents'][0]}
        If not in manual, say: "Please contact support@aurasmart.com."
        """
        
        response = client.models.generate_content(model='gemini-1.5-flash', contents=[system_prompt, user_query])
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")

print("🤖 Aura Support Agent is attempting to connect...")
while True:
    try:
        print(f"Connected to @{bot.get_me().username}")
        bot.polling(none_stop=True, timeout=90)
    except Exception as e:
        print(f"❌ Connection error: {e}. Retrying...")
        time.sleep(10)