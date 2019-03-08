all: transcript

transcript: pull.py
	/usr/local/bin/proxychains4 /usr/local/bin/python3 pull.py
	git add --all
	git commit -v -m "Pull transcript from cnn10 $(shell date "+%Y-%m-%d")"
	git push -u origin master

