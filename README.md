# Проектное задание: ETL
```Итоговая работа третьего спринта специальности "Middle python-разработчик" на обучающей платформе Яндекс.Практикум```

Этот сервис автоматически переносит данные, обновляемые через административную 
панель Django, в Elasticsearch с целью использования полнотекстового поиска. 

Реализована отказоустойчивость при потере связи с ES или Postgres.

Приложение хранит состояние загрузки, т.е. при перезапуске приложения оно продолжает работу с места остановки, а не начинать процесс сканирование БД заново.

# Запуск приложения
- Склонируйте репозитарий:
```
git clone git@github.com:dcomrad/new_admin_panel_sprint_3
```
- Установите Docker согласно инструкции с официального сайта: _https://docs.docker.com/_
- В папке infra/ создайте файлы с переменными окружения, необходимыми для корректной работы приложения.
Структура и названия переменных представлены в файлах .*.env.example:
```
.django.env         - переменные Django-приложения.
.elastic.env        - переменные Elasticsearch.
.nginx.env          - переменные Nginx-сервера.
.postgres.env       - Переменные для подключения к БД postgres. Используются для всех компонентов приложения.
.etl.env            - Переменные ETL-приложения.
    PAGE_SIZE       - Размер пачки данных, обрабатываемых и загружаемых в Elasticsearch.
    UPDATE_PERIOD   - Периодичность проверки наличия обновлённых записей в БД postgres в секундах.
```
- В папке infra выполните следующую команду:
```
sudo docker compose up
```
- Административная панель приложения доступна по адресу http://localhost/
- Elasticsearch API достуаен по адресу http://localhost:9200/