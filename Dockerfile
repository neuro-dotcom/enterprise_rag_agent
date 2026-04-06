FROM python:3.11-slim

WORKDIR /app

# Standard Setup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files (including knowledge_base.md)
COPY . .

# Run the bot directly
CMD ["python", "main.py"]