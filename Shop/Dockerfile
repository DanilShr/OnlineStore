FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./diploma_shop .

COPY ./nginx .

CMD ["uvicorn", "diploma_shop.asgi:application", "--host", "0.0.0.0", "--port", "8000"]