FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Amazon RDS CA bundle, used to verify the database's TLS certificate (set DB_SSL_CA=/certs/rds-global-bundle.pem)
ADD https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem /certs/rds-global-bundle.pem

COPY . .
RUN chmod +x entrypoint.sh && useradd --create-home --uid 10001 appuser && chmod 644 /certs/rds-global-bundle.pem
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
