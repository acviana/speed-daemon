black:
	black speed_daemon
	black tests

black-diff:
	black speed_daemon --diff
	black tests --diff

build:
	docker build -f Dockerfile --tag speed-daemon:latest .

count:
	ls data/*.json | wc

export:
	poetry export -f requirements.txt -o requirements.txt
	poetry export -f requirements.txt -o requirements_dev.txt --dev

install:
	poetry install

pre-commit: black test export build

_sync:
	./sync.sh

sync: _sync count

run-container: build
	docker container run -p 8501:8501 -d speed-daemon:latest

run-server:
	streamlit run speed-daemon/app.py

test:
	pytest -vvs --cov-report term-missing --cov=speed_daemon tests/

_update:
	poetry update

update: _update export pre-commit

update-diff:
	poetry update --dry-run | grep -i updat
