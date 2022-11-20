export PYTHONPATH=./

.PHONY: bot
bot:
	python bot.py

.PHONY: install
install:
	pip3 install -r requirements.txt


.PHONY: test
test:
	pytest tests/