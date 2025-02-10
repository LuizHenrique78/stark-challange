FROM python:3.9-slim

# Install system dependencies (e.g., build tools)
RUN apt-get update && apt-get install -y build-essential

# Create a working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]