CREATE TABLE IF NOT EXISTS GameConfig
(
    id            SERIAL PRIMARY KEY,
    game_running  BOOLEAN     DEFAULT FALSE,
    real_round    INTEGER     DEFAULT 0,
    flag_lifetime INTEGER CHECK ( flag_lifetime > 0 ),
    game_hardness FLOAT CHECK ( game_hardness >= 1 ),
    inflation     BOOLEAN,
    round_time    INTEGER CHECK ( round_time > 0 ),
    mode          VARCHAR(8)  DEFAULT 'classic',
    timezone      VARCHAR(32) DEFAULT 'UTC',
    start_time    TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS Teams
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL DEFAULT '',
    ip          VARCHAR(32)  NOT NULL,
    token       VARCHAR(16)  NOT NULL DEFAULT '',
    highlighted BOOLEAN               DEFAULT FALSE,
    active      BOOLEAN               DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS Tasks
(
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255),
    checker         VARCHAR(1024),
    env_path        VARCHAR(1024),
    gets            INTEGER CHECK ( gets >= 0 ),
    puts            INTEGER CHECK ( puts >= 0 ),
    places          INTEGER CHECK ( places > 0 ),
    checker_timeout INTEGER CHECK ( checker_timeout > 0 ),
    checker_type    VARCHAR(32) DEFAULT 'hackerdom',
    get_period      INTEGER     DEFAULT 0,
    default_score   INTEGER CHECK ( default_score >= 0 ),
    active          BOOLEAN     DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS Flags
(
    id                SERIAL PRIMARY KEY,
    flag              VARCHAR(32) UNIQUE NOT NULL DEFAULT '',
    team_id           INTEGER            NOT NULL REFERENCES Teams ON DELETE RESTRICT,
    task_id           INTEGER            NOT NULL REFERENCES Tasks ON DELETE RESTRICT,
    round             INTEGER            NOT NULL,
    public_flag_data  TEXT               NOT NULL,
    private_flag_data TEXT               NOT NULL,
    vuln_number       INTEGER
);

CREATE TABLE IF NOT EXISTS StolenFlags
(
    flag_id     INTEGER NOT NULL REFERENCES Flags ON DELETE RESTRICT,
    attacker_id INTEGER NOT NULL REFERENCES Teams ON DELETE RESTRICT,
    submit_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (flag_id, attacker_id)
);

CREATE TABLE IF NOT EXISTS TeamTasks
(
    task_id         INTEGER REFERENCES Tasks ON DELETE CASCADE,
    team_id         INTEGER REFERENCES Teams ON DELETE CASCADE,
    status          INTEGER,
    stolen          INTEGER       DEFAULT 0 CHECK ( stolen >= 0 ),
    lost            INTEGER       DEFAULT 0 CHECK ( lost >= 0 ),
    score           FLOAT         DEFAULT 0 CHECK ( score >= 0 ),
    checks          INTEGER       DEFAULT 0,
    checks_passed   INTEGER       DEFAULT 0,
    public_message  TEXT NOT NULL DEFAULT '',
    private_message TEXT NOT NULL DEFAULT '',
    command         TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (team_id, task_id),
    CONSTRAINT sla_valid CHECK ( checks >= 0 AND checks_passed >= 0 AND checks_passed <= checks )
);

CREATE TABLE IF NOT EXISTS TeamTasksLog
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

CREATE TABLE IF NOT EXISTS ScheduleHistory
(
    id       VARCHAR(32) PRIMARY KEY,
    last_run TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_flags_round_team
    ON Flags (round, team_id);

CREATE INDEX IF NOT EXISTS idx_flags_round_task
    ON Flags (round, task_id);
