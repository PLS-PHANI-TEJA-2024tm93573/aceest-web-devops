
# ACEest Web DevOps

A robust, production-ready web application for ACEest, built with Flask and designed for extensibility, maintainability, and modern DevOps best practices. This project features a comprehensive CI/CD pipeline, containerization, and a well-documented API for seamless collaboration and deployment.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Local Development Setup](#local-development-setup)
- [Testing](#testing)
- [API Reference](#api-reference)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
ACEest Web DevOps is a client management and progress tracking platform. It enables fitness professionals to manage clients, log workouts, track progress, and generate reports. The application is built with Flask, uses Docker for containerization, and leverages both Jenkins and GitHub Actions for CI/CD automation.

---

## Architecture
- **Backend:** Python (Flask), modular blueprint structure
- **Frontend:** Jinja2 templates, Bootstrap CSS (customizable)
- **Database:** SQLite (default, can be swapped)
- **Containerization:** Docker & Docker Compose
- **Testing:** Pytest, coverage reporting
- **CI/CD:** Jenkins, GitHub Actions

---

## Local Development Setup

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- (Recommended) Virtualenv

### 1. Clone the Repository
```bash
git clone <repo-url>
cd aceest-web-devops
```

### 2. Install Dependencies
#### Using Virtualenv
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### Or, with Docker Compose
```bash
docker-compose up --build
```

### 3. Run the Application
#### With Python
```bash
python run.py
```
App available at [http://localhost:5000](http://localhost:5000).

#### With Docker
```bash
docker build -t aceest-web-devops:latest .
docker run -p 5000:5000 aceest-web-devops:latest
```

---

## Testing

### Local Python Environment
```bash
pytest --cov=app --cov-report=xml --cov-report=html tests/
```

### Dockerized Testing
```bash
docker build -t aceest-web-devops-test:latest -f test.Dockerfile .
docker run --rm aceest-web-devops-test:latest
```
- Coverage reports: `coverage.xml`, `htmlcov/`

---

## API Reference

- See [`API_ROUTES.md`](./API_ROUTES.md) for a full Markdown reference of all API endpoints, request/response types, and authentication requirements.
- For machine-readable OpenAPI 3.x spec, see [`openapi.yaml`](./openapi.yaml).

---

## CI/CD Pipeline

### Jenkins
- **Linting:** `flake8` for code style
- **Build Validation:** Python syntax check
- **Docker Build:** Main and test images
- **Testing:** All tests in Docker
- **Push:** On `main`, pushes Docker image to Docker Hub

### GitHub Actions
- **Build & Lint:** Installs dependencies, runs `flake8`
- **Docker Build:** Builds app image
- **Automated Testing:** Runs tests in Docker, uploads coverage
- **Jenkins Integration:** Triggers Jenkins build, waits for result
- **Docker Push:** On tag, builds and pushes Docker image

- See [CI/CD Documentation](./CI_CD_Overview.md) for more details.

---

## Contributing

Contributions are welcome! Please:
- Fork the repo and create a feature branch
- Write clear, maintainable code and add tests
- Document new endpoints in `API_ROUTES.md` and update `openapi.yaml` as needed
- Open a pull request with a clear description

---

## License

Distributed under the MIT License. See `LICENSE` for details.

---

## Additional Notes
- Test configuration: `pytest.ini`
- Coverage: XML and HTML
- Flask environment variables: Dockerfile, docker-compose.yml
- Secrets: Managed via GitHub Actions secrets