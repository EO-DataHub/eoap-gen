package := eoap_gen

install:
	poetry install
check:
	poetry run black --preview --check ${package}
	poetry run flake8 ${package}
	poetry run isort --check --diff ${package}
	poetry run pyright
test:
	poetry run pytest -v --cov=./ --cov-report=xml
