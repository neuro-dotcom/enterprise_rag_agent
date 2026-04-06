import os
import telebot
import chromadb
import time
import socket
from google import genai
from dotenv import load_dotenv

# ==========================================
# 🛑 THE DNS BYPASS (Hugging Face Workaround)
# ==========================================
# This tells Python: "Don't ask the server where Telegram is. 
# Go directly to this specific IP address."
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    if args[0] == 'api.telegram.org':
        # 149.154.167.220 is a primary IP for the Telegram Bot API
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('149.154.167.220', 443))]
    return orig_getaddrinfo(*args, **kwargs)
socket.getaddrinfo = patched_getaddrinfo
# ==========================================

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("CRITICAL ERROR: Missing API keys in .env!")

# Connect to the Brain
print("Connecting to Vector Database...")
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_collection(name="aura_manual")

client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_support_query(message):
    try:
        user_query = message.text
        embed_response = client.models.embed_content(
            model='gemini-embedding-001',
            contents=user_query
        )
        query_vector = embed_response.embeddings[0].values
        results = collection.query(query_embeddings=[query_vector], n_results=2)
        retrieved_text = "\n\n".join(results['documents'][0])
        
        system_prompt = f"""
        You are an expert Level 1 Customer Support AI for Aura Smart Home Systems.
        Answer the user's question using ONLY the following official manual text.
        If the answer is not in the text, you must say: "I cannot find this in the manual. Please escalate to human support at support@aurasmart.com."
        
        OFFICIAL MANUAL TEXT:
        {retrieved_text}
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[system_prompt, user_query]
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error handling message: {e}")
        bot.reply_to(message, "I'm having trouble connecting to my knowledge base. Try again in a second.")

print("🤖 Aura Support Agent is attempting to bypass DNS and connect...")

while True:
    try:
        bot_user = bot.get_me()
        print(f"✅ CONNECTED: Bot @{bot_user.username} is online via DNS bypass!")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)