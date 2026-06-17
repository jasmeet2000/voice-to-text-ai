# Placeholder Dockerfile
# Fill in runtime base image and GPU support as needed.
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
