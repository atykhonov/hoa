.PHONY: all test clean activate-virtual-env update-test-server

test:
	./manage.py test -w test/osbb -s

activate-virtual-env:
	export WORKON_HOME=/var/www/.virtualenvs
	source /usr/bin/virtualenvwrapper.sh
	workon hoa

update-test-server: activate-virtual-env
	git pull
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	pip install -r test-requirements.txt
	./manage.py migrate
