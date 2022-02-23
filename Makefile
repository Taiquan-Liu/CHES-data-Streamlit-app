SHELL := /bin/bash

current_dir = $(shell pwd)

lint:
	darker --revision=origin/master... --isort ./*.py

venv-create:
	env_management/create_env.sh

docker-build:
	docker build -t ches-data-streamlit-app:latest .

docker-run:
	docker run -p 8501:8501 ches-data-streamlit-app:latest

local-run:
	source ${current_dir}/.venv/bin/activate && streamlit run app.py
