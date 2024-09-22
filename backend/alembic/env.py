import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine
)
from sqlalchemy.engine import Connection

from alembic import context

from app.v1.core.config import settings
from app.v1.users import User
from app.v1.chats import Message
from app.v1.rooms import Room

DB_URL = settings.db_url_async

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# sets the sqlalchemy.url option in the alembic configuration dynamically
config.set_main_option(
    name="sqlalchemy.url",
    value=DB_URL
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.v1.database.session import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(connection: Connection) -> None:
    """
    Runs the migrations using a given database connection.
    For sync
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations(engine: AsyncEngine) -> None:
    """
    Runs the migrations using a given database engine.
    For async
    """
    async with engine.connect() as connection:
        await connection.run_sync(run_sync_migrations)

    await engine.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Checks if a connection is already available in the Alembic context.
    engine = config.attributes.get("connection", None)

    # Creates an asynchronous engine if one isn't provided.
    if not engine:
        engine = create_async_engine(
            url=DB_URL,
            future=True,
            poolclass=pool.NullPool
        )

    if isinstance(engine, AsyncEngine):
        # run the asynchronous migrations if the engine is asynchronous
        asyncio.run(run_async_migrations(engine))
    else:
        # run the synchronous migrations if the engine is synchronous
        run_sync_migrations(engine.connect())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
