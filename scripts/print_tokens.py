import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

conn = storage.get_db_pool().getconn()
cursor = conn.cursor()

query = "SELECT name, token from teams"

cursor.execute(query)
result = cursor.fetchall()

print('\n'.join(f"{name}:{token}" for name, token in result))

storage.get_db_pool().putconn(conn)
