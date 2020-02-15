FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD docker_config/await_start.sh /await_start.sh
ADD docker_config/db_check.py /db_check.py
ADD docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

ADD backend /app

ADD ./docker_config/gevent_flag_submitter/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
