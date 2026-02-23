FROM python:3.12-alpine

WORKDIR /src

RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    unixodbc-dev \
    && rm -rf /var/cache/apk/*

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./src /src


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

