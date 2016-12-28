.PHONY: all test clean

test:
	./manage.py test -w test/osbb -s
