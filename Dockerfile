FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt


RUN pip install  -r requirements.txt
# Copy the rest of the application code
COPY . .

# Default command starts the Lexia-compatible API server with streaming
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
