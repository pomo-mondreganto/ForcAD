from datetime import datetime
from typing import Optional

from lib.storage import utils

SELECT_LAST_RUN = 'SELECT last_run FROM ScheduleHistory WHERE id=%(id)s'

UPDATE_LAST_RUN = '''
INSERT INTO ScheduleHistory (id, last_run)
VALUES (%(id)s, %(last_run)s)
ON CONFLICT (id) DO
UPDATE SET last_run = EXCLUDED.last_run
'''


def get_last_run(schedule_id: str) -> Optional[datetime]:
    with utils.db_cursor() as (_, curs):
        curs.execute(
            SELECT_LAST_RUN,
            {'id': schedule_id},
        )
        result = curs.fetchone()

    return result[0] if result else None


def set_last_run(schedule_id: str, last_run: datetime) -> None:
    with utils.db_cursor() as (conn, curs):
        curs.execute(
            UPDATE_LAST_RUN,
            {'id': schedule_id, 'last_run': last_run},
        )
        conn.commit()
