# ForcAD
-----------------
That is a pure-python distributable Attack-Defence CTF platform, created to be easily set up.

## Running

5 easy steps to start a game (assuming current working directory to be the project root): 

1. Open `backend/config/config.yml` file 
(or copy `backend/config/config.yml.example` to `backend/config.yml`, if the latter is missing).

2. Add teams and tasks to corresponding config sections following the example's format.

3. Change default passwords (that includes `storages.db.password` for database and `flower.password` for
`celery` visualization).

4. Run `./setup_config.py` to transfer config variables

5. Run `docker-compose up --build` to start the system. Wait patiently for the images to build, it could take a few minutes,
but happens only once. 

That's all! Now you should be able to access scoreboard at `http://0.0.0.0:8080/`.

## Checkers

Checksystem is completely compatible with Hackerdom checkers, but some config-level enchancements were added (see below).
Checkers are configured for each task independently. It's recommended to put each checker in a separate folder 
under `checkers`. Checker is considered to consist of the main executable and some auxiliary files in the same folder.

Possible configuration variables: 

- `checker`: path to the main checker executable (relative to `checkers` folder)

- `gets`: number of flags to put for each team for each round

- `puts`: number of flags to check from the last `flag_lifetime` rounds (see global config for lifetime description). 

- `places`: large tasks may contain a lot of possible places for a flag, that is the number. It'll be passed to checker.

- `checker_timeout`: timeout for **each** checker action

- `checker_returns_flag_id`: whether the checker returns new `flag_id` for the `GET` action for this flag, or the 
passed `flag_id` should be used when getting flag (see more in checker writing section)

## Writing a checker

Checker is an app that checks whether the team's task is running normally, puts flags and then checks them after a few rounds. 

Actions and arguments are passed to checker as command-line arguments, first one is always command type, second is team host.

Checker should terminate with one of the five return codes: 

- **101**: `OK` code, everything works
- **102**: `MUMBLE`, service nor working correctly
- **103**: `CORRUPT`, service is working correctly, but isn't returning flags from previous rounds
- **104**: `DOWN`, could not connect normally
- **-1337**: `CHECKER_ERROR`, unexpected error in checker

All other return codes are considered to be `CHECKER_ERROR`.

In case of unsuccessful invocation `stdout` output will be shown on scoreboard, `stderr` output is considered be debug info
and is stored in database. Also, in case of `CHECKER_ERROR` celery prints warning to console with detailed logs. 

Checker must implement three main actions: 

- `CHECK`: checks that team's service is running normally. Visits some pages, checks registration, login, etc...

Example invocation: `/checkers/task/check.py check 127.0.0.1`

- `PUT`: puts a flag to the team's service. `PUT` is *not* run if `CHECK` failed

Example invocation: `/checkers/task/check.py put 127.0.0.1 <flag_id> <flag> <vuln_number>`

If the checker returns `flag_id` (see checker config), it should write some data 
which helps to access flag later (username, password, etc) to `stdout`. Otherwise, it should use `flag_id` as some "seed" 
to generate such data (on the next invocation `flag_id` will be the same if `checker_returns_flag_id` is set to `false`).
