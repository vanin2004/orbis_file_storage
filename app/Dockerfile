FROM python:3.12-alpine

# RUN apk add --no-cache \
#     build-base \
#     postgresql-dev

RUN mkdir -p /app

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /

CMD ["python", "-m", "app.main"]