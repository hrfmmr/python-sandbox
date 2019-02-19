setup:
	PIPENV_VENV_IN_PROJECT=1 pipenv install -e .

clean:
	pipenv run python daemonize/clean.py

.PHONY: clean
