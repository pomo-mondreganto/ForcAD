FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=${PYTHONPATH}:/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY docker_config/await_start.sh /await_start.sh
COPY docker_config/db_check.py /db_check.py
COPY docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

COPY backend /app

COPY ./docker_config/services/functions.sh /functions.sh
COPY ./docker_config/services/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
