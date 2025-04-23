# CounselAI-Pro: In-Depth Legal Contract Analysis

## Project Description

CounselAI-Pro is a cutting-edge microservice designed to provide ultra-deep, jurisdiction-aware, and clause-level analysis of legal contracts. It goes far beyond simple summaries, offering detailed insights into obligations, rights, risks, and regulatory compliance. Leveraging advanced NLP and LLM techniques, CounselAI-Pro helps legal professionals, businesses, and individuals understand and manage their contracts effectively.

## Key Features

*   **Ultra-Deep Contract Comprehension:**
    *   Clause extraction, typing, and graph building.
    *   Obligation and right mapping.
    *   Ambiguity and inconsistency detection.
    *   Risk scoring and regulatory compliance checks.
*   **Advanced NLP & LLM Workflows:**
    *   Retrieval-augmented reasoning with precedent contracts.
    *   LLM-powered legal reasoning and memo generation.
    *   "Drill-Down Q&A" for in-depth analysis.
*   **Feature-Rich API:**
    *   Ingestion endpoints for PDF/DOCX documents.
    *   Analysis endpoints for clauses, obligations, risks, comparisons, legal memos, and Q&A.
    *   Metadata and monitoring endpoints.
*   **Security & Observability:**
    *   JWT+RBAC, encryption, rate limiting.
    *   Structured logging, metrics, distributed tracing.
*   **Dev-Ops & CI/CD:**
    *   Comprehensive testing (unit/integration).
    *   GitHub Actions for CI/CD.
    *   Docker/K8s deployment support.

## Architecture

*(Diagram to be added here)*

## Setup Instructions

1.  **Prerequisites:**
    *   Python 3.12+
    *   Docker
    *   (Optional) Kubernetes/Helm
2.  **Installation:**

    ```bash
    # Clone the repository
    git clone [repository_url]
    cd contract_service

    # Create a virtual environment (recommended)
    python3.12 -m venv venv
    source venv/bin/activate

    # Install dependencies using pip
    pip install -r requirements.txt
    ```

3.  **Configuration:**

    *   Create a `.env` file in the root directory based on the `.env.example` file.
    *   Set the environment variables according to your needs. See the Configuration section below for more details.

## Running the Application

1.  **Start the FastAPI application:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

    This command starts the FastAPI application using Uvicorn, a production-ready ASGI server. The `--reload` flag enables auto-reloading, which is useful during development.

2.  **Access the API:**

    *   Open your browser and navigate to `http://localhost:8000/docs` to access the automatically generated OpenAPI documentation.
    *   You can use this documentation to test the API endpoints.

## Configuration

The application is configured using environment variables. Here is a list of the available environment variables:

*   `APP_NAME`: The name of the application. Default: `CounselAI-Pro`
*   `ADMIN_EMAIL`: The email address of the administrator. Default: `admin@example.com`
*   `ITEMS_PER_USER`: The number of items per user. Default: `50`
*   `ENVIRONMENT`: The environment the application is running in. Default: `development`
*   `LOG_LEVEL`: The log level. Default: `INFO`
*   `JWT_SECRET`: The secret key used to sign JWT tokens. Default: `super-secret-jwt-key`
*   `PII_ENCRYPTION_KEY`: The encryption key used to encrypt PII data. Default: `sixteen byte key`
*   `DATABASE_URL`: The URL of the database. Default: `sqlite:///./test.db`
*   `MODEL_PATH`: The path to the machine learning models. Default: `/models`
*   `FEATURE_FLAG_SEMANTIC_SEARCH`: Whether to enable semantic search. Default: `false`
*   `FEATURE_FLAG_ADVANCED_RISK`: Whether to enable advanced risk analysis. Default: `false`
*   `FEATURE_FLAG_PII_DETECTION`: Whether to enable PII detection. Default: `true`
*   `ENABLE_ENCRYPTION`: Whether to enable encryption. Default: `false`
*   `ALLOWED_ORIGINS`: A comma-separated list of allowed origins for CORS. Default: `*`

## Testing

To run the tests, use the following command:

```bash
pytest
```

This command runs the tests using pytest. The tests are located in the `tests/` directory.

## Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t counselai-pro .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -d -p 8000:8000 counselai-pro
    ```

## Kubernetes

1.  **Install Helm:**

    ```bash
    # Follow the instructions on the Helm website to install Helm: https://helm.sh/docs/intro/install/
    ```

2.  **Deploy the application using Helm:**

    ```bash
    helm install counselai-pro ./deploy/helm
    ```

## Understanding the Codebase

The codebase is structured as follows:

*   `api/`: This directory contains the API endpoints defined using FastAPI.
    *   `__init__.py`: An empty file that makes the directory a Python package.
    *   `dependencies.py`: Defines dependencies used in the API endpoints, such as database connections and user authentication.
    *   `routers.py`: Defines the API routers, which map URL paths to handler functions.
*   `core/`: This directory contains core application logic, such as configuration and database management.
    *   `__init__.py`: An empty file that makes the directory a Python package.
    *   `config.py`: Defines the application settings using Pydantic.
    *   `database.py`: Defines the database connection and table creation logic.
*   `models/`: This directory contains the Pydantic models used to define the data structures used in the API.
    *   `clause.py`: Defines the `Clause` model, which represents a clause in a contract.
    *   `contract.py`: Defines the `Contract` model, which represents a contract.
    *   `legal_memo.py`: Defines the `LegalMemo` model, which represents a legal memo.
    *   `obligation.py`: Defines the `Obligation` model, which represents an obligation in a contract.
    *   `right.py`: Defines the `Right` model, which represents a right in a contract.
    *   `risk_report.py`: Defines the `RiskReport` model, which represents a risk report for a contract.
*   `services/`: This directory contains the services used to implement the application logic.
    *   `__init__.py`: An empty file that makes the directory a Python package.
    *   `clause_extraction.py`: Implements the clause extraction service, which extracts clauses from a contract text.
    *   `document_metadata.py`: Implements the document metadata service, which extracts metadata from a document.
    *   `obligation_mapping.py`: Implements the obligation mapping service, which maps obligations and rights from a list of clauses.
    *   `risk_scoring.py`: Implements the risk scoring service, which scores clauses and generates a risk report.
    *   `document_retrieval.py`: Implements the document retrieval service, which retrieves similar documents from the database.
    *   `document_upload.py`: Implements the document upload service, which processes uploaded files.
*   `utils/`: This directory contains utility functions used throughout the application.
    *   `__init__.py`: An empty file that makes the directory a Python package.
    *   `logging.py`: Defines the logging configuration.
*   `main.py`: This file contains the main application logic, including the FastAPI application factory.
*   `requirements.txt`: This file lists the dependencies required to run the application.
*   `Dockerfile`: This file defines the steps required to build a Docker image for the application.
*   `docker-compose.yml`: This file defines the services that make up the application, such as the FastAPI application and the Redis database.
*   `tests/`: This directory contains the unit tests for the application.
    *   `test_api.py`: Contains the unit tests for the API endpoints.

## Altering the Codebase

To alter the codebase, follow these steps:

1.  **Identify the component you want to change.**
2.  **Make the necessary changes to the code.**
3.  **Run the tests to ensure that your changes haven't introduced any errors.**
4.  **Commit your changes to the repository.**

## Improving Accuracy

To improve the accuracy of the results, follow these steps:

1.  **Improve the clause extraction service.** This service is responsible for extracting clauses from a contract text. You can improve the accuracy of this service by using more sophisticated NLP techniques.
2.  **Improve the document metadata service.** This service is responsible for extracting metadata from a document. You can improve the accuracy of this service by using more sophisticated NLP techniques.
3.  **Improve the obligation mapping service.** This service is responsible for mapping obligations and rights from a list of clauses. You can improve the accuracy of this service by using more sophisticated NLP techniques.
4.  **Improve the risk scoring service.** This service is responsible for scoring clauses and generating a risk report. You can improve the accuracy of this service by using more sophisticated machine learning techniques.
5.  **Improve the document retrieval service.** This service is responsible for retrieving similar documents from the database. You can improve the accuracy of this service by using more sophisticated semantic search techniques.

## Next Steps

Here are some potential next steps for this project:

*   Implement the LLM-powered legal reasoning workflows.
*   Implement the "Drill-Down Q&A" endpoints.
*   Implement the JWT+RBAC security.
*   Implement the rate limiting.
*   Implement the encryption-at-rest (Fernet).
*   Implement the detailed request/response tracing (OpenTelemetry).
*   Implement the GitHub Actions for CI/CD.
*   Implement the Helm chart for Kubernetes deployment.
*   Implement the OpenAPI spec.
*   Implement the README with architecture diagram and sample payloads.
*   Implement the deployment guide.
