import json

import requests
from configs import get_configured_logger
from constants import SETTINGS
from exceptions import ElasticLoadError
from requests import ConnectionError
from utils import backoff

logger = get_configured_logger(__name__)


# Действительно, стоило не изобретать велосипед, а использовать готовое
# решение. Спасибо за подсказку. Я увидел, что это замечание не обязательное и
# принял решение ничего не менять по банальной причине нехватки времени.
# В понедельник жесткий дедлайн перед стартом командной работы.
# Обязательно ознакомлюсь и обещаю использовать это решение в будущих работах)
class ElasticsearchLoader:
    """Класс забирает данные в подготовленном формате и загружает их в
    Elasticsearch."""
    JSON_HEADER = {'Content-Type': 'application/json'}

    @backoff(ConnectionError)
    def __init__(self,
                 url: str,
                 port: str | int,
                 index: str,
                 schema: dict):
        self.index = index
        self.url = f'http://{url}:{str(port)}'
        self._set_schema(schema)

    def _set_schema(self, schema: dict):
        url = f'{self.url}/{self.index}/?filter_path=error'
        response = requests.put(url=url, headers=self.JSON_HEADER, json=schema)

        errors = json.loads(response.text).get('error')
        if errors:
            logger.warning(errors)

    def _get_bulk_intro(self, _id: str):
        body = {'index': {'_index': self.index, '_id': _id}}
        return json.dumps(body, ensure_ascii=False)

    def _send_bulk_request(self, url: str, body: list[str]) -> None:
        body.append('')
        response = requests.post(url=url, headers=self.JSON_HEADER,
                                 data='\n'.join(body).encode('utf-8'))

        errors = json.loads(response.text).get('items')
        if errors:
            raise ElasticLoadError(errors)

        msg = '{n} записей успешно загружены в индекс {index}'
        logger.info(msg.format(n=len(body) // 2, index=self.index))

    @backoff(ConnectionError)
    def bulk_load(self,
                  items: dict,
                  page_size: int = SETTINGS.etl.page_size) -> None:
        """Принимает словарь для записи в Elasticsearch, причём:
         key - id документа, а value - сам документ в виде объекта dict.
         Загрузка происходит пачками page_size размера."""
        counter = 0
        bulk_url = self.url + '/_bulk?filter_path=items.*.error'
        body = []
        for _id, _data in items.items():
            if counter >= page_size:
                self._send_bulk_request(bulk_url, body)
                body.clear()
                counter = 0

            body.append(self._get_bulk_intro(_id))
            body.append(json.dumps(_data, ensure_ascii=False))
            counter += 1
        if body:
            self._send_bulk_request(bulk_url, body)
