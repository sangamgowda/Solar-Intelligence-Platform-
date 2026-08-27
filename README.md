# Solar Prediction Application

## Objective
The Solar Prediction Application is an enterprise-grade full-stack system designed to forecast solar energy generation based on weather data and other relevant features. It provides robust endpoints for weather data, solar predictions, and comprehensive analytics, leveraging machine learning for accurate forecasting.

## Architecture

The project has been architected following Clean Architecture and SOLID principles, ensuring scalability and maintainability:

* **Frontend:** Built using modern web technologies (Vite/Node.js) providing a responsive user interface to view predictions and analytics.
* **Backend (FastAPI):** A highly scalable backend utilizing FastAPI for high-performance REST APIs. 
    * `src/api/v1/endpoints`: Controllers for `/weather`, `/predictions`, and `/analytics`.
    * `src/ml`: Contains the machine learning inference engine and feature engineering capabilities.
    * `src/services`: Mediates business logic between the API, ML models, and the database.
    * `src/db`: SQLAlchemy configuration and ORM models for data persistence.
* **Security & Configuration:** All configurations are dynamically loaded via `pydantic-settings` using environment variables. Input validation is strictly enforced using Pydantic schemas.

## How to Run the Project

### Quick Start (Windows)
We provide an automated script that handles the entire setup (installing Python, Node.js, dependencies) and starts the servers automatically.

1. Open the project root folder.
2. Double-click the **`RUN_PROJECT.bat`** file.
3. The script will automatically configure your environment. If prompted to install Python or Node.js, accept by typing `Y`.

Once started, the application will be available at:
* **Frontend UI**: http://localhost:5173
* **Backend API**: http://localhost:8000
* **API Documentation (Swagger UI)**: http://localhost:8000/docs

### Docker Deployment (Advanced)
If you prefer containerization, you can run the entire stack using Docker Compose.

```bash
docker-compose up --build
```

## Usage
* Access the **Frontend UI** to interact with the application visually.
* Developers can interact with the **Backend API** programmatically. Explore the endpoints via the built-in Swagger documentation at `http://localhost:8000/docs`.

## Future Scaling Recommendations
* **Database:** The application currently uses SQLite for simplicity, but is fully compatible with PostgreSQL. Change the `SQLALCHEMY_DATABASE_URL` environment variable to migrate.
* **Observability:** Integrate OpenTelemetry or MLflow for advanced telemetry and tracing of ML models.
* **Deployment:** The backend is modular enough to be seamlessly deployed via Kubernetes.
