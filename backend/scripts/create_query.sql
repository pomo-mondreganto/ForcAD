CREATE TABLE IF NOT EXISTS Teams
(
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(255) NOT NULL DEFAULT '',
    ip    VARCHAR(32)  NOT NULL,
    token VARCHAR(16)  NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS Flags
(
    id          SERIAL PRIMARY KEY,
    flag        VARCHAR(32) UNIQUE NOT NULL DEFAULT '',
    team_id     INTEGER            NOT NULL,
    task_id     INTEGER            NOT NULL,
    round       INTEGER            NOT NULL,
    flag_data   TEXT               NOT NULL,
    vuln_number INTEGER
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
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(255),
    checker                 VARCHAR(1024),
    env_path                VARCHAR(1024),
    gets                    INTEGER,
    puts                    INTEGER,
    places                  INTEGER,
    checker_timeout         INTEGER,
    checker_returns_flag_id BOOLEAN,
    gevent_optimized        BOOLEAN,
    get_period              INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS TeamTasks
(
    id              SERIAL PRIMARY KEY,
    round           INTEGER,
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
    command         TEXT NOT NULL DEFAULT '[]',
    UNIQUE (round, task_id, team_id)
);

CREATE TABLE IF NOT EXISTS GlobalConfig
(
    id            SERIAL PRIMARY KEY,
    game_running  BOOLEAN    DEFAULT false,
    real_round    INTEGER    DEFAULT 0,
    flag_lifetime INTEGER,
    game_hardness FLOAT,
    inflation     BOOLEAN,
    round_time    INTEGER,
    game_mode     VARCHAR(8) DEFAULT 'classic'
);

CREATE INDEX IF NOT EXISTS idx_teamtasks_team_task_ids
    ON TeamTasks (team_id, task_id, round);

CREATE INDEX IF NOT EXISTS idx_teamtasks_round
    ON TeamTasks (round);

CREATE INDEX IF NOT EXISTS idx_stolenflags_attacker_flag_id
    ON StolenFlags (attacker_id, flag_id);

CREATE INDEX IF NOT EXISTS idx_flags_team_round
    ON Flags (round, team_id);


DROP FUNCTION IF EXISTS calculate(FLOAT, FLOAT, FLOAT, BOOLEAN);
DROP FUNCTION IF EXISTS recalculate_rating(INTEGER, INTEGER, INTEGER, INTEGER);

CREATE OR REPLACE FUNCTION calculate(FLOAT, FLOAT, FLOAT, BOOLEAN)
    RETURNS TABLE
            (
                attacker_delta FLOAT,
                victim_delta   FLOAT
            )
AS
'rs.so',
'calculate'
    LANGUAGE C STRICT
               ROWS 1;

CREATE OR REPLACE FUNCTION recalculate_rating(att_id INTEGER, vic_id INTEGER, t_id INTEGER, f_id INTEGER)
    RETURNS TABLE
            (
                attacker_delta FLOAT,
                victim_delta   FLOAT
            )
AS
$$
DECLARE
    rround         INTEGER;
    hardness       FLOAT;
    inflate        BOOLEAN;
    attacker_score FLOAT;
    victim_score   FLOAT;
    att_d          FLOAT;
    vic_d          FLOAT;
BEGIN
    SELECT real_round, game_hardness, inflation FROM globalconfig WHERE id = 1 INTO rround, hardness, inflate;

--     avoid deadlocks by locking min(attacker, victim), then max(attacker, victim)
    if att_id < vic_id THEN
        SELECT score
        FROM teamtasks
        WHERE team_id = att_id
          AND task_id = t_id
          AND round = rround FOR NO KEY UPDATE
        INTO attacker_score;

        SELECT score
        FROM teamtasks
        WHERE team_id = vic_id
          AND task_id = t_id
          AND round = rround FOR NO KEY UPDATE
        INTO victim_score;
    ELSE
        SELECT score
        FROM teamtasks
        WHERE team_id = vic_id
          AND task_id = t_id
          AND round = rround FOR NO KEY UPDATE
        INTO victim_score;

        SELECT score
        FROM teamtasks
        WHERE team_id = att_id
          AND task_id = t_id
          AND round = rround FOR NO KEY UPDATE
        INTO attacker_score;
    END IF;


    SELECT * FROM calculate(attacker_score, victim_score, hardness, inflate) INTO att_d, vic_d;

    INSERT INTO stolenflags (attacker_id, flag_id) VALUES (att_id, f_id);

    UPDATE teamtasks
    SET stolen = stolen + 1,
        score  = score + att_d
    WHERE team_id = att_id
      AND task_id = t_id
      AND round >= rround;

    UPDATE teamtasks
    SET lost  = lost + 1,
        score = score + vic_d
    WHERE team_id = vic_id
      AND task_id = t_id
      AND round >= rround;

    attacker_delta := att_d;
    victim_delta := vic_d;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql ROWS 1;
