FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the API Gateway port
EXPOSE 8000

CMD ["python", "ethosguard/gateway/server.py"]
