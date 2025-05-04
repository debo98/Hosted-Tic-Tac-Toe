# Dockerfile for Tic-Tac-Toe FastAPI WebSocket prototype
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Expose port
EXPOSE 3000

# Start the server
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "3000"]
