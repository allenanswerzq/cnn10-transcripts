all: transcript

transcript: pull.py
	python3 pull.py
	git add --all
	git commit -v -m "Pull transcript from cnn10 $(shell date "+%Y-%m-%d")"

