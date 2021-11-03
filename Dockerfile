FROM python:3.9-alpine

COPY . /app

RUN apk add sassc && python3 -m pip install --upgrade pip && python3 -m pip install -r /app/requirements.pip

WORKDIR /app
EXPOSE 8080

ENTRYPOINT ["python3", "-m", "pelican", "-o", "/app/output", "-s", "/app/pelicanconf.py", "--autoreload",  "--listen", "--port", "8080", "--bind", "0.0.0.0"]
