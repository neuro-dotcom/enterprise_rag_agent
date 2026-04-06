FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Give the system permission to run our start script
RUN chmod +x start.sh

# Run the start script instead of the bot directly
CMD ["./start.sh"]