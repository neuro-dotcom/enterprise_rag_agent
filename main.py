import os
import telebot
import chromadb
from google import genai
from dotenv import load_dotenv

# 1. Load Environment & Connect to APIs
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("CRITICAL ERROR: Missing API keys in .env!")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GOOGLE_API_KEY)

# 2. Connect to the Brain (ChromaDB)
print("Connecting to Vector Database...")
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_collection(name="aura_manual")

# 3. The Greeting
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "👋 Welcome to Aura Smart Home Support.\n\nI am an AI agent trained on the official Aura Technical Manual. How can I help you today?"
    bot.reply_to(message, welcome_text)

# 4. The RAG Engine (The core enterprise logic)
@bot.message_handler(func=lambda message: True)
def handle_support_query(message):
    user_query = message.text
    
    # Step A: Convert user question to math
    embed_response = client.models.embed_content(
        model='gemini-embedding-001',
        contents=user_query
    )
    query_vector = embed_response.embeddings[0].values
    
    # Step B: Search the Brain for the closest matching paragraphs
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2 # Retrieve the top 2 most relevant chunks
    )
    
    # Step C: Extract the raw text from the database results
    retrieved_text = "\n\n".join(results['documents'][0])
    
    # Step D: The "Strict Constraint" Prompt
    # We force Gemini to act as an agent and ONLY use our data
    system_prompt = f"""
    You are an expert Level 1 Customer Support AI for Aura Smart Home Systems.
    Answer the user's question using ONLY the following official manual text.
    If the answer is not in the text, you must say: "I cannot find this in the manual. Please escalate to human support at support@aurasmart.com."
    Do not make up information or use outside knowledge. Keep it professional.
    
    OFFICIAL MANUAL TEXT:
    {retrieved_text}
    """
    
    # Step E: Generate the final answer using the standard text model
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[system_prompt, user_query]
    )
    
    bot.reply_to(message, response.text)

print("🤖 Aura Support Agent is online and listening...")
bot.polling(none_stop=True)