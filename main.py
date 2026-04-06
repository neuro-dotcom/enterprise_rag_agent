import os
import telebot
import chromadb
import time
from google import genai
from dotenv import load_dotenv

# 1. Load Environment & Connect to APIs
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("CRITICAL ERROR: Missing API keys in .env!")

# 2. Connect to the Brain (ChromaDB)
print("Connecting to Vector Database...")
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_collection(name="aura_manual")

client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 3. The RAG Engine
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
        bot.reply_to(message, "I encountered a technical glitch. Please try again in a moment.")

# 4. ROBUST STARTUP LOOP
print("🤖 Aura Support Agent is attempting to connect to Telegram...")

while True:
    try:
        # Test the connection before starting
        bot_user = bot.get_me()
        print(f"✅ CONNECTED: Bot @{bot_user.username} is online!")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Retrying in 15 seconds...")
        time.sleep(15)