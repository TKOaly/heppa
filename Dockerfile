FROM python:3.8-alpine

WORKDIR /heppa

COPY requirements.txt requirements.txt
RUN apk add --no-cache build-base \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del --no-cache build-base

COPY . .

# Compile translation binary files
RUN pybabel compile -d application/translations

CMD ["gunicorn", "--preload", "--workers", "1", "--bind", "0.0.0.0:8000", "application:app"]