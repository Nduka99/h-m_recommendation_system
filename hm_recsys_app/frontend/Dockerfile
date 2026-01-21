FROM python:3.9-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .

EXPOSE 8503

CMD ["streamlit", "run", "app.py", "--server.port", "8503", "--server.address", "0.0.0.0"]
