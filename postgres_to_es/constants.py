from pathlib import Path

from pydantic import BaseModel, BaseSettings, Field

BASE_DIR = Path(__file__).parent


class ETLSettings(BaseSettings):
    page_size: int
    update_period: int


class PostgresSettings(BaseSettings):
    dbname: str = Field(env='PG_DB_NAME')
    user: str = Field(env='PG_DB_USER')
    password: str = Field(env='PG_DB_PASSWORD')
    host: str = Field(env='PG_DB_HOST')
    port: int = Field(env='PG_DB_PORT')
    options: str = '-c search_path=content'


class ElasticSettings(BaseSettings):
    host: str = Field(env='ES_HOST')
    port: int = Field(env='ES_PORT')
    index: str = Field(env='ES_INDEX')
    schema_file: str = Field(env='ES_SCHEMA_FILE')


class LoggerSettings(BaseModel):
    log_file = BASE_DIR / 'etl.log'
    format = '"%(asctime)s - [%(levelname)s] - %(message)s"'
    dt_format = '%d.%m.%Y %H:%M:%S'


class Settings(BaseSettings):
    etl: ETLSettings = ETLSettings()
    pg_dsn: PostgresSettings = PostgresSettings()
    elastic: ElasticSettings = ElasticSettings()
    logger: LoggerSettings = LoggerSettings()


SETTINGS = Settings()
