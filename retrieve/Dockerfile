FROM python:3.11.15-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8002

CMD ["uvicorn", "app.retrieve_main:app", "--host","0.0.0.0","--port","8002"]

