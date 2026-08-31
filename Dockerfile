FROM python:3.12-slim

# System deps for psycopg2 (PostgreSQL) build
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "analytics_dashboard.wsgi:application", "--bind", "0.0.0.0:8000"]