install:
			pip install --upgrade pip &&\
			pip install -r requirements.txt

test:
		python -m pytest -vv --cov=app tests

format:
		black *.py

lint:
		pylint --disable=R,C *.py
