import json
from dataclasses import asdict
from json import JSONDecodeError
from time import sleep
from typing import Iterable

from constants import SETTINGS
from exceptions import ElasticLoadError
from extract import PostgresExtractor
from load import ElasticsearchLoader
from state import JsonFileStorage, State
from transform import Transformer
from utils import backoff


def persons_names_handler(persons: Iterable) -> list:
    return [person.name for person in persons]


def persons_handler(persons: Iterable) -> list[dict]:
    return [asdict(person) for person in persons]


def get_es_schema(file_path: str) -> dict:
    with open(file_path, 'rt') as file:
        try:
            return json.load(file)
        except JSONDecodeError:
            return {}


@backoff(ElasticLoadError)
def main():
    extractor = PostgresExtractor(State(JsonFileStorage('state.txt')),
                                  SETTINGS.pg_dsn.dict(),
                                  SETTINGS.etl.page_size)

    transformer = Transformer()
    transformer.add_handler('id', None, str)
    transformer.add_handler('rating', 'imdb_rating', None)
    transformer.add_handler('genres', 'genre', list)
    transformer.add_handler('actors', 'actors_names', persons_names_handler)
    transformer.add_handler('actors', None, persons_handler)
    transformer.add_handler('writers', 'writers_names', persons_names_handler)
    transformer.add_handler('writers', None, persons_handler)
    transformer.add_handler('directors', 'director', persons_names_handler)

    loader = ElasticsearchLoader(SETTINGS.elastic.host,
                                 SETTINGS.elastic.port,
                                 SETTINGS.elastic.index,
                                 get_es_schema(SETTINGS.elastic.schema_file))

    while True:
        for filmwork in extractor.get_filmworks():
            data = transformer.transform(filmwork, 'id')
            loader.bulk_load(data)
        sleep(SETTINGS.etl.update_period)


if __name__ == '__main__':
    main()
