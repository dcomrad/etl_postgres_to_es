import abc
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    """Класс для хранения состояния при работе с данными, чтобы постоянно не
    перечитывать данные с начала. Здесь представлена реализация с сохранением
    состояния в файл."""
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        Path(__file__).parent.joinpath(file_path).touch(exist_ok=True)

    def save_state(self, state: dict) -> None:
        new_state = self.retrieve_state()
        new_state.update(state)
        with open(self.file_path, 'wt') as file:
            json.dump(new_state, file)

    def retrieve_state(self) -> dict:
        with open(self.file_path, 'rt') as file:
            try:
                return json.load(file)
            except JSONDecodeError:
                return {}


class State:
    """Класс-интерфейс для класса-хранилища состояния"""

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state().get(key, None)
