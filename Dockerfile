FROM python:3.8-slim

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*

ADD . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt