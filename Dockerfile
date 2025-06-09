FROM python:3.12.1-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=1

WORKDIR /project

RUN apk update && \
    apk add --no-cache python3-dev gcc musl-dev libpq-dev nmap

COPY pyproject.toml poetry.lock ./


RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . /app/
COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh
