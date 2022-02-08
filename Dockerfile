FROM python:3.9.10-slim-buster

COPY env_management/requirements.txt .

RUN pip install -r requirements.txt