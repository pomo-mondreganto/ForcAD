import os

import kombu
import psycopg2
import sys

amqp_host = os.environ['RABBITMQ_HOST']
amqp_user = os.environ['RABBITMQ_DEFAULT_USER']
amqp_port = os.environ['RABBITMQ_PORT']
amqp_pass = os.environ['RABBITMQ_DEFAULT_PASS']
amqp_vhost = os.environ['RABBITMQ_DEFAULT_VHOST']

broker_url = f'amqp://{amqp_user}:{amqp_pass}@{amqp_host}:{amqp_port}/{amqp_vhost}'

c = kombu.Connection(broker_url)
c.connect()

conn = psycopg2.connect(
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
)
curs = conn.cursor()

query = 'SELECT COUNT(id) from globalconfig'
try:
    curs.execute(query)
except psycopg2.ProgrammingError:
    sys.exit(1)
initialized, = curs.fetchone()

# Exit with 0 if initialized
sys.exit(initialized == 0)
