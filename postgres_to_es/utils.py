from functools import wraps
from time import sleep

from configs import get_configured_logger

logger = get_configured_logger(__name__)


def backoff(exception, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если
    возникла ошибка. Использует наивный экспоненциальный рост времени повтора
    (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        time = start_sleep_time * 2^(n) if time < border_sleep_time
        time = border_sleep_time if time >= border_sleep_time
    :param exception: тип ошибки, который перехвачивает функция
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                inner.fail_count = 0
                return result
            except exception as ex:
                time = start_sleep_time * pow(factor, inner.fail_count)
                if time > border_sleep_time:
                    time = border_sleep_time
                else:
                    inner.fail_count += 1
                msg = 'Сбой вызова {function}: {msg}. Повтор через {time} с.'
                logger.error(msg.format(function=func.__name__,
                                        msg=str(ex).replace('\n', ' '),
                                        time=time))
                sleep(time)
                inner(*args, **kwargs)

        inner.fail_count = 0
        return inner
    return wrapper
