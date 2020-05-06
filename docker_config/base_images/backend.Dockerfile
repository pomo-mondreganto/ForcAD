FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq-dev

COPY backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY docker_config/await_start.sh /await_start.sh
COPY docker_config/db_check.py /db_check.py
COPY docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######