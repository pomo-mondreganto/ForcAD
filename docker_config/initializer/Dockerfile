FROM python:3.7-alpine

RUN apk add gcc make musl-dev postgresql-dev

ADD ./backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD backend /app

ADD ./docker_config/initializer/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ADD ./docker_config/db_check.py /db_check.py

CMD ["/entrypoint.sh"]