ve:
	python3 -m venv .ve; \
	. .ve/bin/activate; \
	pip install -r requirements.txt

docker_build:
	docker-compose up -d --build

docker_build_postgres:
	docker-compose up -d postgres --build

docker_up:
	docker-compose up -d

docker_down:
	docker-compose down

docker_restart:
	docker-compose stop
	docker-compose up -d

docker_logs:
	docker-compose logs --tail=100 -f

runserver:
	uvicorn conduit.app:app --host 0.0.0.0

runserver-dev:
	export APP_ENV=dev && uvicorn conduit.app:app --host 0.0.0.0 --reload

test:
	export APP_ENV=test && python -m pytest -v ./tests

test-cov:
	export APP_ENV=test && python -m pytest  --cov=./conduit ./tests

install_hooks:
	pip install -r requirements-ci.txt; \
	pre-commit install

run_hooks:
	pre-commit run --all-files

style:
	flake8 conduit

format:
	black conduit --check

types:
	mypy --namespace-packages -p "conduit" --config-file setup.cfg

types-tests:
	mypy --namespace-packages -p "tests" --config-file setup.cfg

lint:
	flake8 conduit
	isort conduit --diff
	black conduit --check
	mypy --namespace-packages -p "conduit" --config-file setup.cfg

migration:
	alembic revision --autogenerate -m "$(message)"

migrate:
	alembic upgrade head
