import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAGE_SIZE = int(os.getenv('PAGE_SIZE'))
UPDATE_PERIOD = int(os.getenv('UPDATE_PERIOD'))

PG_DSN = {
    'dbname': os.getenv('PG_DB_NAME'),
    'user': os.getenv('PG_DB_USER'),
    'password': os.getenv('PG_DB_PASSWORD'),
    'host': os.getenv('PG_DB_HOST'),
    'port': os.getenv('PG_DB_PORT'),
    'options': '-c search_path=content'
}

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / 'etl.log'
LOGGER_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOGGER_DT_FORMAT = '%d.%m.%Y %H:%M:%S'

ES_HOST = os.getenv('ES_HOST')
ES_PORT = os.getenv('ES_PORT')
ES_INDEX = os.getenv('ES_INDEX', 'movies')
ES_SCHEMA_FILE = os.getenv('ES_SCHEMA_FILE', 'es_schema.txt')
