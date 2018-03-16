install:
	pip3 install -r requirements.txt

lint:
	python3 -m pylint default_vpc_killer/ -r n && \
	python3 -m pycodestyle default_vpc_killer/ --max-line-length=120
