lint:
	darker --revision=origin/master... --isort ./*.py

venv-create:
	env_management/create_env.sh

venv-run:
	env_management/run_env.sh