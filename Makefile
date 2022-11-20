
.PHONY: bot
bot:
	python3.9 bot.py

.PHONY: install
install:
	apt install libsqlite3-dev
	# yum install -y gcc make sqlite-devel zlib-devel libffi-devel openssl-devel
	pip3 install -r requirements.txt

