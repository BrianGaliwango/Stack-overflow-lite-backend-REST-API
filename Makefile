install:
			pip install --upgrade pip &&\
			pip install -r requirements.txt

test:
		pytest -vv -s --cov=app tests


format:	
			black *.py

lint:
		pylint --disable=R,C *.py							

format:
		black *.py

lint:
		pylint --disable=R,C *.py

