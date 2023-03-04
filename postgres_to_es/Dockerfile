FROM python:3.10

ENV WORKDIR /app

WORKDIR $WORKDIR

COPY . .

RUN rm -f Dockerfile && \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    groupadd -r etl && \
    useradd -d $WORKDIR -r -g etl etl && \
    chown etl:etl -R $WORKDIR && \
    chmod +x wait-for-it.sh

USER etl

ENTRYPOINT ["./wait-for-it.sh", "db:5432", "--strict", "elasticsearch:9200", "--strict", "--", "python", "etl.py"]