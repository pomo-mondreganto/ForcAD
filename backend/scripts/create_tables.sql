CREATE TABLE IF NOT EXISTS Teams
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL DEFAULT '',
    ip          VARCHAR(32)  NOT NULL,
    token       VARCHAR(16)  NOT NULL DEFAULT '',
    highlighted BOOLEAN               DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Flags
(
    id                SERIAL PRIMARY KEY,
    flag              VARCHAR(32) UNIQUE NOT NULL DEFAULT '',
    team_id           INTEGER            NOT NULL,
    task_id           INTEGER            NOT NULL,
    round             INTEGER            NOT NULL,
    public_flag_data  TEXT               NOT NULL,
    private_flag_data TEXT               NOT NULL,
    vuln_number       INTEGER
);

CREATE TABLE IF NOT EXISTS StolenFlags
(
    id          SERIAL PRIMARY KEY,
    flag_id     INTEGER NOT NULL,
    attacker_id INTEGER NOT NULL,
    submit_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
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
    checker_timeout INTEGER,
    checker_type    VARCHAR(32) DEFAULT 'hackerdom',
    get_period      INTEGER     DEFAULT 0
);

CREATE TABLE IF NOT EXISTS TeamTasks
(
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER,
    team_id         INTEGER,
    status          INTEGER,
    stolen          INTEGER       DEFAULT 0,
    lost            INTEGER       DEFAULT 0,
    score           FLOAT         DEFAULT 0,
    checks          INTEGER       DEFAULT 0,
    checks_passed   INTEGER       DEFAULT 0,
    public_message  TEXT NOT NULL DEFAULT '',
    private_message TEXT NOT NULL DEFAULT '',
    command         TEXT NOT NULL DEFAULT '',
    UNIQUE (task_id, team_id)
);

CREATE UNLOGGED TABLE IF NOT EXISTS TeamTasksLog
(
    id              SERIAL PRIMARY KEY,
    round           INTEGER,
    task_id         INTEGER,
    team_id         INTEGER,
    status          INTEGER,
    stolen          INTEGER                  DEFAULT 0,
    lost            INTEGER                  DEFAULT 0,
    score           FLOAT                    DEFAULT 0,
    checks          INTEGER                  DEFAULT 0,
    checks_passed   INTEGER                  DEFAULT 0,
    public_message  TEXT NOT NULL            DEFAULT '',
    private_message TEXT NOT NULL            DEFAULT '',
    command         TEXT NOT NULL            DEFAULT '',
    ts              TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS GlobalConfig
(
    id            SERIAL PRIMARY KEY,
    game_running  BOOLEAN     DEFAULT false,
    real_round    INTEGER     DEFAULT 0,
    flag_lifetime INTEGER,
    game_hardness FLOAT,
    inflation     BOOLEAN,
    round_time    INTEGER,
    game_mode     VARCHAR(8)  DEFAULT 'classic',
    timezone      VARCHAR(32) DEFAULT 'UTC',
    start_time    TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_flags_round_team
    ON Flags (round, team_id);

CREATE INDEX IF NOT EXISTS idx_flags_round_task
    ON Flags (round, task_id);
