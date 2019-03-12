all: transcript

transcript: pull.py
	/usr/local/bin/proxychains4 /usr/local/bin/python3 pull.py
	./push.sh
