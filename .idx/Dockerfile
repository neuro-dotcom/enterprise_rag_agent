# ==========================================
# STAGE 1: The Builder (Creates the Brain)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install the dependencies needed to build the database
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ingestion script and the manual
COPY build_brain.py .
COPY knowledge_base.md .

# We must pass the API key into this stage so it can talk to Google to embed the text
ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY

# Run the script to generate the chroma_db folder
RUN python build_brain.py


# ==========================================
# STAGE 2: The Runtime (Runs the Bot)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Re-install dependencies (since Stage 2 is a fresh OS)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the files needed to run the bot
COPY main.py .

# THE MAGIC TRICK: Copy the built brain from Stage 1 into Stage 2
COPY --from=builder /app/chroma_db ./chroma_db

# Run the Telegram Bot
CMD ["python", "main.py"]