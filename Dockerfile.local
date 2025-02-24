FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get remove -y gcc && apt-get autoremove -y

COPY alembic .
COPY alembic.ini .
COPY app .
COPY entrypoint.sh .
COPY gunicorn.conf.py .

RUN chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app

EXPOSE 8000

STOPSIGNAL SIGINT

CMD ["gunicorn", "--config=gunicorn.conf.py", "-b", "0.0.0.0:8000", "app.main:app"]
