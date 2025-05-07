FROM python:3.12-slim

RUN apt-get update \ 
    && apt-get install -y --no-install-recommends \  build-essential libpq-dev \
     && pip install --no-cache-dir --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

EXPOSE 8004

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8004"]