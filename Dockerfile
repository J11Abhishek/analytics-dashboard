FROM python:3.12-slim

# System deps for psycopg2 (PostgreSQL) and weasyprint (PDF export)
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
