FROM python:3.9

ENV PYTHONUNBUFFERED=1

COPY src/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY src /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
