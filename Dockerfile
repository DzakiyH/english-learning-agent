FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Pre-seed the Oxford 3000/5000 vocabulary database into the container
RUN python seed_oxford.py

# Start the Telegram bot
CMD ["python", "bot.py"]
