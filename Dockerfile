FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY . .

# Render sets $PORT dynamically; HF Spaces expects 7860.
# Default to 7860 locally/HF, Render overrides via $PORT at runtime.
ENV PORT=7860
EXPOSE 7860

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}