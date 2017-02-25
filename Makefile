.PHONY: all test clean

test:
	./manage.py test -w test/osbb -s

update-test-server:
	git pull
	workon hoa
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	pip install -r test-requirements.txt
	./manage.py migrate
