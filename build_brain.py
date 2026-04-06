import os
import chromadb
from google import genai
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("CRITICAL ERROR: GOOGLE_API_KEY not found in .env")

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# 2. Initialize the Vector Database (ChromaDB)
print("Initializing ChromaDB...")
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection(name="aura_manual")

# 3. Read and Chunk the Knowledge Base
print("Reading knowledge_base.md...")
with open("knowledge_base.md", "r", encoding="utf-8") as file:
    text = file.read()

# Chop the document into chunks by double line breaks (paragraphs)
chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

# 4. Embed and Store the Data
print(f"Found {len(chunks)} chunks. Generating embeddings...")

for i, chunk in enumerate(chunks):
    # Convert text to mathematical vectors using Google's embedding model
    response = client.models.embed_content(
        model='gemini-embedding-001',
        contents=chunk
    )
    vector = response.embeddings[0].values
    
    # Save the vector and the original text into the database
    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[vector],
        documents=[chunk]
    )

print("✅ SUCCESS: The Vector Database has been built. The AI now has a memory.")