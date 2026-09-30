from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.database import Base

# Importante: importar os models para o Alembic "enxergar" as tabelas.
# Toda vez que você criar um model novo, adicione o import aqui.
from app.models import User  # noqa: F401

# Configuração do Alembic
config = context.config

# Carrega a URL do banco a partir do nosso .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configuração de logging do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos nossos models (base para autogenerate)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline: gera SQL sem conectar no banco (útil para revisar)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Roda as migrações dentro de uma conexão já estabelecida."""

    def include_object(object, name, type_, reflected, compare_to):
        """
        Filtro: ignora tabelas do PostGIS que não são nossas.
        Sem isso, o Alembic tenta dropar tabelas de sistema.
        """
        if type_ == "table":
            # Tabelas que pertencem ao PostGIS / sistema
            excluded_tables = {
                "spatial_ref_sys",
                "topology",
                "layer",
                "state",
                "county",
                "county_lookup",
                "countysub_lookup",
                "cousub",
                "place",
                "place_lookup",
                "addr",
                "addrfeat",
                "bg",
                "edges",
                "faces",
                "featnames",
                "tabblock",
                "tabblock20",
                "tract",
                "zcta5",
                "zip_lookup",
                "zip_lookup_all",
                "zip_lookup_base",
                "zip_state",
                "zip_state_loc",
                "pagc_gaz",
                "pagc_lex",
                "pagc_rules",
                "geocode_settings",
                "geocode_settings_default",
                "loader_lookuptables",
                "loader_platform",
                "loader_variables",
                "direction_lookup",
                "secondary_unit_lookup",
                "street_type_lookup",
                "state_lookup",
            }
            if name in excluded_tables:
                return False

        return True

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,  # ← filtro mágico
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Modo online: conecta no banco via engine assíncrona e aplica."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Wrapper síncrono para o Alembic chamar nosso fluxo async."""
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
