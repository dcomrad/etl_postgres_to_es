from dataclasses import dataclass, fields
from typing import Any, Callable, Iterable, Optional

from pydantic import BaseModel


class Transformer:
    """Класс принимает данные во внутреннем формате и преобразовывать
    структуру и формат, пригодные для записи в Elasticsearch"""
    @dataclass(frozen=True)
    class Handler:
        field_name: Optional[str]
        func: Optional[Callable]

    def __init__(self):
        self.handlers = {}

    def add_handler(self,
                    field_name: str,
                    new_name: Optional[str] = None,
                    handler: Optional[Callable] = None) -> None:
        """Задаёт обработчик для последующей обработки полученных элементов.
        Args:
            field_name (str): Имя поля исходного объекта

            new_name (str): Новое имя поля. Если None, исходное имя не меняется

            handler (callable):
                Функция для преобразования значения. Если None, сохраняется
                исходное значение
        """
        if field_name not in self.handlers:
            self.handlers[field_name] = {self.Handler(new_name, handler)}
        else:
            self.handlers[field_name].add(self.Handler(new_name, handler))

    def transform(self, items: Iterable, key_field: str) -> dict[str: dict]:
        """Обрабатывает элементы items и возвращает словарь, где ключом
        является item[key_field], а значением сам item, преобразованный
        обработчиками, предварительно заданными методом add_handler"""
        result = {}
        for item in items:
            element = {}

            item_fields = self._get_item_fields(item)

            for field in item_fields.difference(self.handlers.keys()):
                # поля, для которых нет обработчика, переносим без изменений
                element[field] = self._get_item_value(item, field)

            for field in item_fields.intersection(self.handlers.keys()):
                handlers = self.handlers[field]
                for handler in handlers:
                    name = handler.field_name or field
                    value = self._get_item_value(item, field)
                    element[name] = (handler.func(value)
                                     if handler.func else value)
            result[element[key_field]] = element
        return result

    @staticmethod
    def _get_item_fields(item: Any) -> set[Any]:
        """Возвращает перечень полей item."""
        if isinstance(item, dict):
            return set(item.keys())
        elif isinstance(item, BaseModel):
            return set(item.__fields__.keys())
        else:
            return set(field.name for field in fields(item))

    @staticmethod
    def _get_item_value(item: Any, field: str) -> Any:
        """Возвращает значение поля аргумента item."""
        try:
            return item.get(field)
        except AttributeError:
            return getattr(item, field)
