---
title: Enterprise RAG Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 🤖 Enterprise RAG Support Agent 

An autonomous, cloud-deployed AI Support Agent built for Telegram. This bot utilizes Retrieval-Augmented Generation (RAG) to provide highly accurate, hallucination-free technical support strictly grounded in official documentation.

## ⚙️ Architecture & Tech Stack
* **AI Engine:** Google Gemini 2.5 Flash (for rapid, reasoning-based generation)
* **Embeddings:** Gemini-Embedding-001
* **Vector Database:** ChromaDB (for semantic memory and document retrieval)
* **Interface:** Telegram Bot API (`pyTelegramBotAPI`)
* **Infrastructure:** Docker, Hugging Face Spaces
* **Database (RBAC):** Local persistent JSON ledger for user state.
* **Network Ops:** Flask-based health checks, IPv4 forced routing, and hardcoded DNS bypass for cloud resilience.

## 🚀 Key Features
1. **Strict Context Grounding:** The bot is instructed to answer *only* using the provided `knowledge_base.md`. Out-of-domain questions are respectfully escalated to human support.
2. **Dynamic Vector Ingestion:** The ChromaDB database is built at runtime. Updating the AI's knowledge is as simple as modifying the markdown file.
3. **Role-Based Access Control (RBAC):** Secured via Telegram Chat ID verification to prevent unauthorized API quota drain. Includes a built-in `/admin` dashboard.
4. **Persistent Demo Quota System:** Admins can securely issue temporary "Guest Passes" allowing recruiters or technical directors exactly 2 queries (ideal for testing 1 in-domain and 1 out-of-domain request) before automatically revoking access via a JSON state ledger.
5. **Zero-Downtime Resilience:** Utilizes custom socket patching and background HTTP ping servers to bypass strict cloud DNS limitations.

## 🛠️ How It Works
1. A user sends a support question via Telegram.
2. The query is embedded into a mathematical vector.
3. ChromaDB performs a similarity search against the technical manual chunks.
4. The closest matching text is injected into a strict system prompt.
5. Gemini generates a localized, accurate response and sends it back to the user.

---
*Developed by neuro-dotcom as an AI Ops portfolio project.*