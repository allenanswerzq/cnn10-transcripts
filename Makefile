all: transcript

transcript: pull.py
		python3 pull.py
		./push.sh
