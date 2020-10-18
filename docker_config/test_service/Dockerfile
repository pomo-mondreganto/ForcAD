FROM python:3.7

ENV PYTHONUNBUFFERED=1

COPY tests/service/src/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY tests/service/src /app

COPY ./docker_config/test_service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
