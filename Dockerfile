FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "orchestrator.py"]
