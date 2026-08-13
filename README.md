# AI-Based Construction Worker Attendance & PPE Compliance Monitoring System

## Python Environment Setup

The project uses a Python virtual environment to keep dependencies isolated and consistent across the development team.

### Step 1 — Create the Virtual Environment

From the project root (`AI-PPE-Construction/`):

```bash
python -m venv .venv
```

This creates an isolated `.venv` directory. The directory is excluded from Git through `.gitignore`.

### Step 2 — Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

After activation, the terminal should indicate that the `.venv` environment is active.

### Step 3 — Upgrade Python Packaging Tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 4 — Install Project Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains the Python libraries currently required by the project.

### Step 5 — Verify the Environment

```bash
python --version
pip list
```

At this stage, the Python environment is ready for the next project setup steps.

> **Note:** PyTorch installation may depend on the available hardware and whether the machine uses CPU or a compatible NVIDIA GPU. The team should use the same tested PyTorch configuration for development.
> **Note:** To exit the virtual environment when you are done working, simply type deactivate in your terminal.

## Database Setup

The project uses PostgreSQL 16 with the `pgvector` extension for storing application data and performing fast facial embedding searches.

### Step 6 — Start PostgreSQL with Docker

**1. Start Docker Desktop**
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed. Open the Docker Desktop application on your computer and wait for the engine to start (the icon in your system tray should indicate it is running).

**2. Configure Environment Variables**
You need a local `.env` file for your database credentials. Run the appropriate command below for your terminal to copy the template:

* **macOS / Linux / PowerShell:**
  ```bash
  cp .env.example .env
Windows (Command Prompt):
copy .env.example .env
Launch the Database
Run this command from the root of the project to download the image and start the database in the background:
docker compose up -d
Verify the Database is Running
Check that the container is healthy and running on port 5432:
docker compose ps
Optional
 If you want to check the database logs to ensure the vector extension initialized properly, run:
docker compose logs db
