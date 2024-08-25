# ![RealWorld Example App](.github/assets/logo.png)


> ### Python / FastAPI codebase containing real world examples (CRUD, auth, middlewares advanced patterns, etc.) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged backend application built with **[FastAPI](https://fastapi.tiangolo.com/)** including CRUD operations, authentication, routing, and more.

For more information on how this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


## Description
This project is a Python-based API that uses PostgreSQL as its database. It includes JWT authentication and is configured using environment variables.

## Prerequisites
- Python 3.12
- FastAPI
- PostgreSQL

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/borys25ol/fastapi-realworld-backend
    cd fastapi-realworld-backend
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv .ve
    source .ve/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    - Create a `.env.local` file in the root directory and add the following:
        ```dotenv
        SECRET_KEY=your_secret_key
        POSTGRES_USER=your_postgres_user
        POSTGRES_PASSWORD=your_postgres_password
        POSTGRES_DB=your_postgres_db
        POSTGRES_HOST=your_postgres_host
        POSTGRES_PORT=your_postgres_port
        JWT_SECRET_KEY=your_jwt_secret_key
        ```

5. **Database setup:**
    - Ensure PostgreSQL is running and create the necessary databases:
        ```sql
        CREATE DATABASE conduit;
        CREATE DATABASE conduit_test;
        ```

## Makefile Commands

The following commands are available in the `Makefile`:

- **docker_build**: Build and start the Docker containers.
    ```sh
    make docker_build
    ```

- **docker_up**: Start the Docker containers.
    ```sh
    make docker_up
    ```

- **docker_down**: Stop the Docker containers.
    ```sh
    make docker_down
    ```

- **runserver**: Run the application server.
    ```sh
    make runserver
    ```

- **test**: Run the tests.
    ```sh
    make test
    ```

- **test-cov**: Run the tests with coverage.
    ```sh
    make test-cov
    ```

- **lint**: Lint the code with flake8, isort, and black.
    ```sh
    make lint
    ```

- **migration**: Create a new database migration.
    ```sh
    make migration message="your_migration_message"
    ```

- **migrate**: Apply database migrations.
    ```sh
    make migrate
    ```
