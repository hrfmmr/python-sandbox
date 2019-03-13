setup:
	LDFLAGS='-L/usr/local/Cellar/portaudio/19.6.0/lib' \
	CFLAGS='-I/usr/local/Cellar/portaudio/19.6.0/include' \
	PIPENV_VENV_IN_PROJECT=1 pipenv install
