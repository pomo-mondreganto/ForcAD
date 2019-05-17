FROM python:3.7-alpine

RUN apk add gcc make musl-dev postgresql-dev

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD ./docker_config/await_start.sh /await_start.sh
ADD ./docker_config/db_check.py /db_check.py
ADD ./docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

RUN apk add socat

ADD backend /app

ADD ./docker_config/tcp_flag_submitter/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]