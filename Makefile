all: test

test:
	nosetests --with-coverage --nocapture --cover-package=sqlalchemy_mptt --cover-erase --with-doctest
