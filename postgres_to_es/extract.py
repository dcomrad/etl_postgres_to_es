from datetime import datetime
from typing import Iterable
from uuid import UUID

import psycopg2
import contextlib
from configs import get_configured_logger
from filmwork import Filmwork, Person
from psycopg2 import OperationalError
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import DictCursor
from state import State
from utils import backoff

logger = get_configured_logger(__name__)


class PostgresExtractor:
    """Класс для извлечения данных из postgres с сохранением состояния."""

    TABLES = ['film_work', 'genre', 'person']

    def __init__(self,
                 state: State,
                 pg_dsn: dict,
                 page_size: int,
                 tables: list | str = 'all'):
        self.state = state
        self.pg_dsn = pg_dsn
        self.page_size = page_size
        self.tables = self.TABLES if tables == 'all' else tables

    @backoff(OperationalError)
    def _get_connection(self) -> pg_connection:
        return psycopg2.connect(**self.pg_dsn, cursor_factory=DictCursor)

    @backoff(OperationalError)
    def _get_table_ids(self, table: str) -> Iterable[Iterable[UUID]]:
        """Возвращает объект-генератор со списком id изменённых записей
        таблицы table. Сохраняет состояние modified, после обработки списка"""
        modified = self.state.get_state(table)

        if modified is None:
            modified = datetime.min
            self.state.set_state(table, str(modified))

        with contextlib.closing(self._get_connection()) as connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT id, modified
                    FROM {table}
                    WHERE modified > '{modified}'
                    ORDER BY modified
                """
                cursor.execute(query.format(table=table, modified=modified))

                while True:
                    rows = cursor.fetchmany(size=self.page_size)
                    if not rows:
                        self.state.set_state(table, str(modified))
                        return
                    modified = rows[-1].get('modified')
                    yield (row.get('id') for row in rows)

    @backoff(OperationalError)
    def _get_filmwork_ids(self, table: str) -> Iterable[Iterable[UUID]]:
        """Возвращает объект-генератор со списком id кинопроизведений, которые
        связаны с изменёнными записями таблицы table."""

        if table == 'film_work':
            for filmwork_ids in self._get_table_ids(table):
                yield (item for item in list(filmwork_ids))
            return

        with contextlib.closing(self._get_connection()) as connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT fw.id
                    FROM film_work fw
                    LEFT JOIN {table}_film_work tfw ON tfw.film_work_id = fw.id
                    WHERE tfw.{table}_id IN ({table_ids})
                """
                for table_ids in self._get_table_ids(table):
                    cursor.execute(
                        query.format(
                            table=table,
                            table_ids=','.join([f"'{id}'" for id in table_ids])
                        )
                    )
                    while True:
                        rows = cursor.fetchmany(size=self.page_size)
                        if not rows:
                            break
                        yield (row.get('id') for row in rows)
                return

    @backoff(OperationalError)
    def get_filmworks(self) -> Iterable[Iterable[Filmwork]]:
        """Возвращает объект-генератор со списком изменённых
        кинопроизведений."""
        query = """
        SELECT
            fw.id fw_id,
            fw.title,
            fw.description,
            fw.rating,
            g.name genre,
            pfw.role,
            p.id p_id,
            p.full_name
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN ({filmwork_ids});
        """
        for table in self.tables:
            for filmwork_ids in self._get_filmwork_ids(table):
                filmwork_ids = ','.join(
                    [f"'{fw_id}'" for fw_id in filmwork_ids]
                )
                if not filmwork_ids:
                    continue

                with contextlib.closing(self._get_connection()) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(query.format(filmwork_ids=filmwork_ids))
                        rows = cursor.fetchall()

                filmworks = {}
                for row in rows:
                    fw_id = row.get('fw_id')
                    if fw_id not in filmworks:
                        filmworks[fw_id] = Filmwork(
                            id=fw_id,
                            title=row.get('title'),
                            description=row.get('description'),
                            rating=row.get('rating'),
                        )

                    filmworks[fw_id].genres.add(row.get('genre'))

                    role = row.get('role')
                    if role:
                        person = Person(id=row.get('p_id'),
                                        name=row.get('full_name'))
                        getattr(filmworks[fw_id], f'{role}s').add(person)

                yield filmworks.values()
