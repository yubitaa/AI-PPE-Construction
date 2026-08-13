from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Make the backend package importable.
#
# Project structure:
# AI-PPE-Construction/
# ├── backend/
# │   └── app/
# └── database/
#     └── migrations/
#         └── env.py
#
# We add "backend/" to Python's import path so that:
#     from app.db.base import Base
# works when Alembic is executed from the project root.
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------------------------
# Load environment variables from the project root .env file.
# ---------------------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

# Alembic Config object.
config = context.config

# ---------------------------------------------------------------------------
# Configure logging from Alembic's generated configuration file.
# ---------------------------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import the SQLAlchemy Base and ALL database models.
#
# Importing the models here is important because Base.metadata must know
# about every table before Alembic can autogenerate migrations.
# ---------------------------------------------------------------------------

from app.db.base import Base
from app.models import (
    Administrator,
    AttendanceRecord,
    DailyReport,
    FaceEmbedding,
    PPEComplianceLog,
    VideoSource,
    Worker,
)

# ---------------------------------------------------------------------------
# Get the PostgreSQL connection URL from .env
# ---------------------------------------------------------------------------

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Please create a .env file in the project root."
    )

# Override the URL from alembic.ini with the value from .env.
config.set_main_option("sqlalchemy.url", database_url)

# ---------------------------------------------------------------------------
# Alembic uses this metadata to detect database schema changes.
# ---------------------------------------------------------------------------

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Offline mode generates SQL without creating a live database connection.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This connects directly to the PostgreSQL database and applies migrations.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()