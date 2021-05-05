from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from pyinaturalist_open_data.models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py, can be acquired:
# my_important_option = config.get_main_option('my_important_option')


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
