# Docker Guide for Urja-Setu

This guide explains how to build, run, and share the Urja-Setu project using Docker.

## 1. Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).

## 2. Running Locally with Docker Compose

To start both the frontend and backend with a single command:

```bash
docker-compose up --build
```

- **Frontend**: Accessible at `http://localhost`
- **Backend API**: Accessible at `http://localhost:8000`

To stop the containers:
```bash
docker-compose down
```

## 3. Collaborative Workflow (Sharing Images)

To share this environment with others without them needing to set up Python or Node.js locally:

### A. Tag and Push to Docker Hub
1. **Login**: `docker login`
2. **Build and Tag**:
   ```bash
   docker build -t your-username/urja-setu-backend ./backend
   docker build -t your-username/urja-setu-frontend --build-arg VITE_API_URL=http://your-backend-url ./frontend
   ```
3. **Push**:
   ```bash
   docker push your-username/urja-setu-backend
   docker push your-username/urja-setu-frontend
   ```

### B. Collaborator Pulls and Runs
Your teammate can then run the project by creating a `docker-compose.yml` and pointing to your images:

```yaml
version: '3.8'
services:
  backend:
    image: your-username/urja-setu-backend
    ports: ["8000:8000"]
  frontend:
    image: your-username/urja-setu-frontend
    ports: ["80:80"]
```

## 4. Notes
- The SQLite database is persisted via a volume mapping in `docker-compose.yml`.
- For production use, ensure `VITE_API_URL` is set to your live backend domain during the build.
