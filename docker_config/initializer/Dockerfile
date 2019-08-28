FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=1

RUN apk add gcc make musl-dev postgresql-dev

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD backend /app

ADD backend/rs_implementation /rs_implementation
WORKDIR /rs_implementation
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /

ADD ./docker_config/initializer/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ADD ./docker_config/db_check.py /db_check.py
ADD ./docker_config/check_initialized.py /check_initialized.py

CMD ["/entrypoint.sh"]