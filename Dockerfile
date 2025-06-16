FROM python:3.12.1-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=1

WORKDIR /app

RUN apk update && \
    apk add --no-cache python3-dev gcc musl-dev libpq-dev nmap

COPY pyproject.toml poetry.lock ./

ENV PIP_DEFAULT_TIMEOUT=100
RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH=/app

COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh
