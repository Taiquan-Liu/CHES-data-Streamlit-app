FROM openjdk:slim
COPY --from=python:3.9.10-slim / /

COPY setup.py .
RUN pip install -e .

EXPOSE 8501

COPY data ./data
COPY utils.py .
COPY app.py .

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
