import os
import telebot
import chromadb
import time
import threading
from flask import Flask
from google import genai
from dotenv import load_dotenv

# 1. THE HEALTH CHECK SERVER (Required by Hugging Face)
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is healthy!", 200

def run_flask():
    # Hugging Face looks for a server on port 7860
    app.run(host='0.0.0.0', port=7860)

# Start the health check in a background thread
threading.Thread(target=run_flask, daemon=True).start()

# 2. LOAD & INITIALIZE
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 3. KNOWLEDGE BASE LOGIC
print("🧠 Checking Knowledge Base...")
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection(name="aura_manual")

# Only build if empty
if collection.count() == 0:
    print("📥 Ingesting manual...")
    with open("knowledge_base.md", "r", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
    for i, chunk in enumerate(chunks):
        res = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
        collection.add(ids=[f"c{i}"], embeddings=[res.embeddings[0].values], documents=[chunk])
    print("✅ Brain built.")

# 4. BOT LOGIC
@bot.message_handler(func=lambda message: True)
def handle_support_query(message):
    try:
        user_query = message.text
        embed_res = client.models.embed_content(model='gemini-embedding-001', contents=user_query)
        results = collection.query(query_embeddings=[embed_res.embeddings[0].values], n_results=2)
        
        system_prompt = f"""
        You are an Aura Smart Home AI. Use this manual text: {results['documents'][0]}
        If not in manual, say: "Please contact support@aurasmart.com."
        """
        
        response = client.models.generate_content(model='gemini-1.5-flash', contents=[system_prompt, user_query])
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")

# 5. RESILIENT POLLING
print("🤖 Aura Support Agent is starting...")
while True:
    try:
        # Check connection
        me = bot.get_me()
        print(f"✅ SUCCESS: Connected to @{me.username}")
        bot.polling(none_stop=True, timeout=90)
    except Exception as e:
        print(f"❌ Connection error: {e}. Retrying in 10s...")
        time.sleep(10)