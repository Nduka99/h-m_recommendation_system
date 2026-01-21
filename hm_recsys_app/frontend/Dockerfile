FROM python:3.9-slim

WORKDIR /app

COPY hm_recsys_app/frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hm_recsys_app/frontend/ .

EXPOSE 8503

CMD ["streamlit", "run", "app.py", "--server.port", "8503", "--server.address", "0.0.0.0"]
