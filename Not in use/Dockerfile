FROM python:3.11-slim

WORKDIR /app
COPY requirements-demo.txt .
RUN pip install --no-cache-dir -r requirements-demo.txt gunicorn

COPY . .

EXPOSE 5000
ENV PORT=5000 PYTHONUNBUFFERED=1

# Serve the hosted demo. It runs fully offline on seed data.
# Set DATAHUB_GMS_URL / DATAHUB_GMS_TOKEN to enable live scans.
CMD ["gunicorn", "--chdir", "webapp", "app:app", "--bind", "0.0.0.0:5000"]
