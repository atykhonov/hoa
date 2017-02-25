.PHONY: all test clean activate-test-virtual-env update-test-server

test:
	./manage.py test -w test/osbb -s

activate-test-virtual-env:
	( \
		export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python; \
		export WORKON_HOME=/var/www/.virtualenvs; \
		. /usr/bin/virtualenvwrapper.sh; \
		workon hoa; \
	)

update-test-server: activate-test-virtual-env
	git pull
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	pip install -r test-requirements.txt
	./manage.py migrate
