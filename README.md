---
title: Enterprise RAG Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 🤖 Enterprise RAG Support Agent 

An autonomous, cloud-deployed AI Support Agent built for Telegram. This bot utilizes Retrieval-Augmented Generation (RAG) to provide highly accurate, hallucination-free technical support strictly grounded in official corporate documentation.

## ⚙️ Architecture & Tech Stack
* **AI Engine:** Google Gemini 2.5 Flash (for rapid, reasoning-based generation)
* **Embeddings:** Gemini-Embedding-001
* **Vector Database:** ChromaDB (for semantic memory and document retrieval)
* **Interface:** Telegram Bot API (`pyTelegramBotAPI`)
* **Infrastructure:** Docker, Hugging Face Spaces
* **State Management:** Local persistent JSON ledger for user state and RBAC.
* **Network Ops:** Flask-based health checks, IPv4 forced routing, and hardcoded DNS bypass for cloud resilience.

## 🚀 Key Features
1. **Strict Context Grounding:** The bot is constrained to answer *only* using the provided `knowledge_base.md`. Out-of-domain questions are respectfully escalated to human support.
2. **Semantic Chunking & Ingestion:** The system automatically splits manuals into logical chunks, converts them to high-dimensional vectors, and stores them in ChromaDB at runtime. Updating the AI's knowledge simply requires modifying the markdown file.
3. **Role-Based Access Control (RBAC):** Secured via Telegram Chat ID verification to prevent unauthorized API quota drain. Includes a built-in `/admin` dashboard.
4. **Persistent Demo Quota System:** Admins can securely issue temporary "Guest Passes." This allows recruiters or tech leads exactly 2 queries (ideal for testing 1 in-domain and 1 out-of-domain request) before automatically revoking access via the JSON state ledger.
5. **Zero-Downtime Resilience:** Utilizes custom socket patching and background HTTP ping servers to bypass strict cloud DNS limitations.

## 🛠️ How It Works (The RAG Pipeline)
1. **Load & Embed:** The system reads `knowledge_base.md` and checks if the ChromaDB collection is empty. If so, it embeds the chunks and stores them locally.
2. **Query:** A user sends a support question via Telegram.
3. **Retrieve:** The query is embedded, and ChromaDB performs a similarity search to find the closest matching technical manual chunks.
4. **Generate:** The matching text is injected into a strict system prompt, forcing Gemini to generate an accurate, localized response based *only* on the retrieved context.

---
*Developed by neuro-dotcom as an AI Ops portfolio project.*