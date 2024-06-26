import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set SQLAlchemy URL from environment variables
database_url = os.getenv('DATABASE_URL')
if database_url is None:
    raise ValueError("DATABASE_URL environment variable is not set")

print(f"--->{database_url}")
config.set_main_option('sqlalchemy.url', database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your models' MetaData object here
# for 'autogenerate' support
from app.db.base import Base
from app.models.email_verification_token import EmailVerificationToken
from app.models.mfa import MFA
from app.models.password_reset_token import PasswordResetToken
from app.models.user_session import UserSession
from app.models.user import User

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is also acceptable
    here. By skipping the Engine creation we don't even need a
    DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
