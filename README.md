# Patients API Project

## Overview

This is a FastAPI-based project designed to provide a patient registration API. The project is containerized using Docker, allowing for easy setup and deployment.

## Features

- Fast and asynchronous API using FastAPI
- Auto-generated documentation with Swagger UI
- Containerized environment with Docker and Docker Compose

## Prerequisites

Ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Running the Project

To start the project, execute the following command in your terminal:

```sh
docker-compose up --build
```

This will build and start the necessary containers.

### API Documentation

Once the project is running, you can access the API documentation via Swagger UI at:

[http://localhost:8000/docs](http://localhost:8000/docs)

or view the raw OpenAPI specification at:

[http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure

```
📂 project-root
 ├── 📂 app        # FastAPI application code
 ├── 📄 Dockerfile # Docker build configuration
 ├── 📄 docker-compose.yml # Docker Compose setup
 ├── 📄 requirements.txt # Python dependencies
 ├── 📄 README.md   # Project documentation
```

## Stopping the Project

To stop the running containers, use:

```sh
docker-compose down
```
