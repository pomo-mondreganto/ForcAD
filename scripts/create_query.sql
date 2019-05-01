CREATE TABLE IF NOT EXISTS Teams
(
  id    SERIAL PRIMARY KEY,
  name  VARCHAR(255) NOT NULL DEFAULT '',
  ip    INET,
  token VARCHAR(16)  NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS Flags
(
  id        SERIAL PRIMARY KEY,
  flag      VARCHAR(32) UNIQUE NOT NULL DEFAULT '',
  team_id   INTEGER            NOT NULL,
  task_id   INTEGER            NOT NULL,
  round     INTEGER            NOT NULL,
  flag_data VARCHAR(255)       NOT NULL
);

CREATE TABLE IF NOT EXISTS StolenFlags
(
  id          SERIAL PRIMARY KEY,
  flag_id     INTEGER NOT NULL,
  attacker_id INTEGER NOT NULL,
  UNIQUE (flag_id, attacker_id)
);

CREATE TABLE IF NOT EXISTS Tasks
(
  id              SERIAL PRIMARY KEY,
  name            VARCHAR(255),
  checker         VARCHAR(1024),
  env_path        VARCHAR(1024),
  gets            INTEGER,
  puts            INTEGER,
  places          INTEGER,
  checker_timeout INTEGER
);

CREATE TABLE IF NOT EXISTS TeamTasks
(
  id        SERIAL PRIMARY KEY,
  round     INTEGER,
  task_id   INTEGER,
  team_id   INTEGER,
  status    INTEGER,
  stolen    INTEGER                DEFAULT 0,
  lost      INTEGER                DEFAULT 0,
  score     FLOAT                  DEFAULT 0,
  up_rounds INTEGER                DEFAULT 0,
  message   VARCHAR(1024) NOT NULL DEFAULT '',
  UNIQUE (round, task_id, team_id)
);

CREATE INDEX IF NOT EXISTS idx_teamtasks_team_task_ids
  ON TeamTasks (team_id, task_id, round);

CREATE INDEX IF NOT EXISTS idx_teamtasks_round
  ON TeamTasks (round);

CREATE INDEX IF NOT EXISTS idx_stolenflags_attacker_flag_id
  ON StolenFlags (attacker_id, flag_id);

CREATE INDEX IF NOT EXISTS idx_flags_team_round
  ON Flags (round, team_id);
