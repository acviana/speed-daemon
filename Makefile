black:
	black speed_daemon
	black tests

black-diff:
	black speed_daemon --diff
	black tests --diff

build:
	docker build -f Dockerfile --tag speed-daemon:latest .

count:
	find data/ -name "*.json" | wc -l

export-requirements:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	poetry export -f requirements.txt -o requirements_dev.txt --dev --without-hashes

flake8:
	flake8 speed_daemon/ tests/ --statistics

install:
	poetry install

pre-commit: black flake8 test build

_sync:
	./sync.sh

sync: _sync count

run-container: build
	docker container run -p 8501:8501 -d speed-daemon:latest

run-server:
	streamlit run speed_daemon/app.py

test:
	pytest -vvs --cov-report term-missing --cov=speed_daemon tests/

_update:
	poetry update

update: _update export pre-commit

# Checks for updated dependencies beyond the pinned Poetry versions
update-check:
	poetry show --outdated -v

update-diff:
	poetry update --dry-run | grep -i updat
