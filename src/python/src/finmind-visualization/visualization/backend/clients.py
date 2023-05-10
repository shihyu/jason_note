from sqlalchemy import create_engine, engine

from visualization import config


def get_redash_mysql_conn() -> engine.base.Connection:
    address = (
        f"mysql+pymysql://{config.REDASH_MYSQL_DATA_USER}:{config.REDASH_MYSQL_DATA_PASSWORD}"
        f"@{config.REDASH_MYSQL_DATA_HOST}:{config.REDASH_MYSQL_DATA_PORT}/{config.REDASH_MYSQL_DATA_DATABASE}"
    )
    engine = create_engine(address)
    connect = engine.connect()
    return connect
