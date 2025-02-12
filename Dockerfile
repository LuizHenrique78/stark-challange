FROM python:3.12.1-alpine3.19

# Install system dependencies (e.g., build tools)
RUN apt-get update && apt-get install -y build-essential

# Create a working directory
WORKDIR /app

ARG API_TOKEN
ENV API_TOKEN=${API_TOKEN}
ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}


ENV DATABASE_URL DATABASE_URL
ENV RABBITMQ_URL RABBITMQ_URL
ENV STARKBANK_PROJECT_ID STARKBANK_PROJECT_ID
ENV STARKBANK_USER_PRIVATE_KEY STARKBANK_USER_PRIVATE_KEY

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]