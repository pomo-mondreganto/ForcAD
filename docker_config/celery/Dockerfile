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

########## CUSTOMIZE ##########

ENV PWNLIB_NOTERM=true

# uncomment blocks to enable features

### selenium (chromedriver) dependencies (from https://github.com/joyzoursky/docker-python-chromedriver) ###
################
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends google-chrome-stable unzip \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
################

COPY ./checkers/requirements.txt /checker_requirements.txt
RUN pip install -r /checker_requirements.txt

COPY ./checkers /checkers

########## END CUSTOMIZE ##########

COPY backend /app

COPY ./docker_config/celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER nobody

CMD ["/entrypoint.sh"]
