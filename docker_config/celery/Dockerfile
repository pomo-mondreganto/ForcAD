FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD backend/rs_implementation /rs_implementation
WORKDIR /rs_implementation
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /

ADD ./docker_config/await_start.sh /await_start.sh
ADD ./docker_config/db_check.py /db_check.py
ADD ./docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

########## CUSTOMIZE ##########

RUN apt-get install -y git libssl-dev libffi-dev build-essential

ADD ./checkers/requirements.txt /checker_requirements.txt
RUN pip install -r /checker_requirements.txt

ADD ./checkers /checkers

ENV PWNLIB_NOTERM=true

########## END CUSTOMIZE ##########

ADD backend /app

ADD ./docker_config/celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER nobody

CMD ["/entrypoint.sh"]