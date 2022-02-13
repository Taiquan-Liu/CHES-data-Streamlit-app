FROM python:3.9.10-slim-buster

COPY setup.py .
RUN pip install -e .

EXPOSE 8501

COPY utils.py .
COPY app.py .

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
