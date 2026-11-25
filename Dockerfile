# Image for Hugging Face Spaces (Docker SDK). Set GROQ_API_KEY as a Space secret.
FROM python:3.12-slim

RUN useradd -m -u 1000 user
WORKDIR /app
ENV PYTHONUNBUFFERED=1 FASTEMBED_CACHE_PATH=/app/.cache/fastembed HF_HUB_DISABLE_TELEMETRY=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag/ rag/
COPY index/ index/
COPY static/ static/
COPY eval/results/ eval/results/
COPY server.py .
# Download the embedding model now, so the first visitor doesn't wait for it.
RUN python -c "from rag.retrieve import embedder; embedder()" && chown -R user /app

USER user
EXPOSE 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers", "--forwarded-allow-ips=*"]
