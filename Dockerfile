FROM python:3.12-slim

RUN mkdir /app
WORKDIR /app

COPY requirements.txt version.py ./

RUN pip install -U pip
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/conduit"

COPY conduit conduit/

EXPOSE 8080
