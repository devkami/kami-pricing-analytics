# Kami Pricing Web Scraping Microservice

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Running Tests](#running_tests)
- [Contributing](#contributing)

## About <a name = "about"></a>

This project is designed to be a scalable Kami Pricing Web Scraping Microservice, initially focused on extracting product seller information from the "Beleza Na Web" marketplace. Built with FastAPI for its asynchronous support and easy-to-use routing, it aims to provide a robust foundation for scraping various marketplaces by extending the service with minimal effort. The project structure supports the SOLID principles, clean code practices, and is ready for Test-Driven Development (TDD) and future scalability considerations, including integration with Celery for task queuing and Traefik for load balancing.

Given your project's Taskipy settings for task automation with Poetry, let's revise the "Getting Started" section to incorporate these tasks into the workflow. This ensures developers are guided to use Taskipy commands for linting, testing, and coverage reporting, enhancing code quality and consistency.

---

## Getting Started <a name="getting_started"></a>

Follow these instructions to set up the project on your local machine for development, testing, and potential contributions. You have the option to run the project locally using Poetry and Taskipy tasks or within a Docker container.

### Prerequisites

- Ensure Python 3.11+ is installed on your system.
- Install [Poetry](https://python-poetry.org/) for dependency management.
- For Docker users, install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/).

### Installing with Poetry

1. **Clone the Repository:**

   ```bash
   git clone https://yourrepository.com/web-scraping-microservice.git
   cd web-scraping-microservice
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Activate Virtual Environment:**

   ```bash
   poetry shell
   ```

4. **Run Linting (Optional):**

   Before starting the server or committing your changes, you can lint your code:

   - To review linting errors without applying changes:

     ```bash
     poetry run task lint-review
     ```

   - To automatically format and sort your imports:

     ```bash
     poetry run task lint
     ```

5. **Start the FastAPI Server:**

   ```bash
   uvicorn scraper.app:app --reload
   ```

   Access the application at `http://localhost:8000` and the Swagger UI at `http://localhost:8000/docs`.

### Running with Docker

Build and run the Docker container:

```bash
docker-compose up --build
```

This makes your FastAPI application accessible at `http://localhost:8001`, with Swagger UI available at `http://localhost:8001/docs`.

## Usage <a name = "usage"></a>

To use the microservice, make a POST request to `/scrap/` with a JSON body containing the `product_url`. For example:

```json
{
  "product_url": "https://www.belezanaweb.com.br/some-product"
}
```

The service will return a JSON response with seller information extracted from the product page.

## Running Tests <a name = "running_tests"></a>

To maintain and verify application functionality:

- **Using Taskipy and Poetry:**

  - To run tests with coverage reporting:

    ```bash
    poetry run task test
    ```

  - Coverage reports are generated in HTML format by the `post_test` task and can be found in the `htmlcov` directory.

- **Using Docker:**

  For Docker users, run tests within the Docker environment:

  ```bash
  docker-compose run web poetry run task test
  ```

## Contributing <a name = "contributing"></a>

We welcome contributions to this project. Please refer to [`CONTRIBUTING.md`](./CONTRIBUTING.md) for more details on how to contribute, coding standards, and the pull request process.
