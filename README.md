# ![RealWorld Example App](.github/assets/logo.png)


> ### Python / FastAPI codebase containing real world examples (CRUD, auth, middlewares advanced patterns, etc.) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged backend application built with **[FastAPI](https://fastapi.tiangolo.com/)** including CRUD operations, authentication, routing, and more.

For more information on how this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


## Description
This project is a Python-based API that uses PostgreSQL as its database.
It is built with FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3 based on standard Python type hints.

## Prerequisites
- Python 3.12
- FastAPI
- PostgreSQL
- Pytest
- Docker

## Installation

Create a virtual environment:

```sh
make ve
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Configuration
--------------

Replace `.env.example` with real `.env`, changing placeholders

```
SECRET_KEY=your_secret_key
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
JWT_SECRET_KEY=your_jwt_secret_key
```

Run with Docker
--------------
You must have ``docker`` and ``docker-compose`` installed on your machine to start this application.

Setup PostgreSQL database with docker-compose:

```sh
make docker_build_postgres
```

Run the migrations:

```sh
make migrate
```

Run the application server:

```sh
make runserver
```

Also, you can run the fully Dockerized application with `docker-compose`:

```sh
make docker_build
```

And after that run migrations:

```sh
docker exec -it conduit-api alembic upgrade head
```

Run tests
---------

Tests for this project are defined in the ``tests/`` folder.

For running tests, you can have to create separate `.env.test` file the same as `.env` file, but with different database name.:

```
POSTGRES_DB=conduit_test
```

Then run the tests:

```sh
make test
```

Or run the tests with coverage:

```sh
make test-cov
```

Run Conduit Postman collection tests
---------

For running tests for local application:

```sh
APIURL=http://127.0.0.1:8000/api ./postman/run-api-tests.sh
```

For running tests for fully Dockerized application:

```sh
APIURL=http://127.0.0.1:8080/api ./postman/run-api-tests.sh
```

Web routes
-----------
    All routes are available on / or /redoc paths with Swagger or ReDoc.
