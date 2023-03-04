FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240

ENV DJANGO_SETTINGS_MODULE 'config.settings'

ENV WORKDIR /app

WORKDIR $WORKDIR

COPY . .

RUN mkdir -p $WORKDIR/static/ && \
    mkdir -p $WORKDIR/media/ && \
    rm -f Dockerfile && \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    groupadd -r web && \
    useradd -d $WORKDIR -r -g web web && \
    chown web:web -R $WORKDIR && \
    chmod +x docker-entrypoint.sh wait-for-it.sh

EXPOSE 8000

#USER web

ENTRYPOINT ["./wait-for-it.sh", "db:5432", "--strict", "--", "uwsgi", "--strict", "--ini", "uwsgi.ini"]