FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=1

ADD backend/tests/service/src/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD backend/tests/service/src /app

ADD ./docker_config/test_service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
