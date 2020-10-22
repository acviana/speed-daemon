black:
	black speed-daemon

build:
	docker build -f Dockerfile --tag speed-daemon:latest .

count:
	ls data/*.json | wc

export:
	poetry export -f requirements.txt -o requirements.txt
	poetry export -f requirements.txt -o requirements_dev.txt --dev

sync:
	./sync.sh

run:
	streamlit run speed-daemon/app.py

update:
	poetry update

update-diff:
	poetry update --dry-run | grep -i updat
