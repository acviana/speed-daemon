black:
	black speed-daemon

build:
	docker build -f Dockerfile --tag speed-daemon:latest .

count:
	ls data/*.json | wc

export:
	poetry export -f requirements.txt -o requirements.txt
	poetry export -f requirements.txt -o requirements_dev.txt --dev

install:
	poetry install

pre-commit: black build

_sync:
	./sync.sh

sync: _sync count

run-container: build
	docker container run -p 8501:8501 -d speed-daemon:latest

run-server:
	streamlit run speed-daemon/app.py

_update:
	poetry update

update: _update export pre-commit

update-diff:
	poetry update --dry-run | grep -i updat
