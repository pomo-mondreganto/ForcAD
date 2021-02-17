![tests](https://github.com/pomo-mondreganto/ForcAD/workflows/tests/badge.svg)

# ForcAD

![Front page](static/front_page.png)

Pure-python distributable Attack-Defence CTF platform, created to be easily set up.

The name is pronounced as "forkád".

#### This documentation is for the latest (development) version of ForcAD. It might not be stable or even working. The latest stable version can be found [here](https://github.com/pomo-mondreganto/ForcAD/releases/latest), see the README.md there.

Note that there's a [wiki](https://github.com/pomo-mondreganto/ForcAD/wiki) containing some useful queries for game
statistics, services description, writing a checker, modifying the rating system, etc.

## Running

5 easy steps to start a game (assuming current working directory to be the project root):

1. Open `config.yml` file
   (or `cp config.yml.example config.yml`, if the latter is missing).

2. Add teams and tasks to corresponding config sections following the example's format, set `start_time`, `timezone` (
   e.g. `Europe/Moscow`) and `round_time` (in seconds) (for recommendations see
   [checker_timeout](#checkers) variable).

3. Install `cli/requirements.txt` (`pip3 install -r cli/requirements.txt`)

4. Run `./control.py setup` to prepare ForcAD config. This command will generate a new login and password
   (if not provided in `admin.username` and `admin.password`) for the admin interface and services. Generated
   credentials will appear in command output and in the updated `config.yml`. Backup of the config file will be
   generated just in case.

5. Run `./control.py start --fast` to start the system. Wait patiently for the images to build, it could take a few
   minutes, but happens only once. Notice that `--fast` option uses the pre-built image, so if you modified the base
   images or backend requirements, omit this option to run the full build.

That's all! Now you should be able to access the scoreboard at `http://127.0.0.1:8080/`. Admin panel is accessible at
`http://127.0.0.1:8080/admin`. Celery visualization (flower) is at `http://127.0.0.1:8080/flower`.

> Before each new game run `./control.py reset` to delete old database and temporary files (and docker networks)

## Configuration and usage

### Receiving flags

Teams are identified by tokens (unique and randomly generated on startup). Look for them in the logs of `initializer`
container or print using the following command after the system started: `./control.py print_tokens`. Token is private
information, so send them to each team correspondingly.

### Flag format

System uses the most common flag format by default: `[A-Z0-9]{31}=`, the first symbol is the first letter of
corresponding service name. You can change flag generation in function `Flag.generate` in
[backend/lib/models/flag.py](backend/lib/models/flag.py)

Each flag is valid (received by flag receivers and can be checked by checker) for `flag_lifetime` rounds (game config
variable).

### Configuration file

Config file (`config.yml`) is split into five main parts:

- **game** contains the following settings:

- `timezone`: the timezone in which `start_time` is specified. Example: `Europe/Moscow`.

- `start_time`: the datetime of game start (timezone will be taken from the `timezone` option).
  Example: `2019-11-30 15:30:00`.

- `default_score`: default score for tasks (float). Example: `2000`.

- `env_path`: string (see [checkers](#checkers) section). Example: `/checkers/bin/`.

- `flag_lifetime`: flag lifetime in rounds (see [flag format](#flag-format) section). Example: `5`.

- `game_hardness`: game hardness parameter (
  see [rating system](https://github.com/pomo-mondreganto/ForcAD/wiki/Rating-system) wiki page). Example: `3000.0`.

- `inflation`: inflation (see [rating system](https://github.com/pomo-mondreganto/ForcAD/wiki/Rating-system) wiki page).
  Example: `true`.

- `checkers_path`: path to checkers inside Docker container. `/checkers/` if not changed specifically.

- **storages** describes settings used to connect to PostgreSQL and Redis (examples provided):

- `db`: PostgreSQL settings:

    - `user: system_admin`
    - `password: **change_me**`
    - `dbname: system_db`
    - `host: postgres`
    - `port: 5432`

- `redis`: Redis (cache) settings:

    - `password: **change_me**`
    - `db: 0`
    - `host: redis`
    - `port: 6379`

- `rabbitmq`: RabbitMQ (broker) settings:

    - `user: system_admin`
    - `password: **change_me**`
    - `host: rabbitmq`
    - `port: 5672`
    - `vhost: forcad`

- **admin** contains credentials to access celery visualization (`/flower/` on scoreboard) and admin panel:

    - `username: system_admin`
    - `password: **change_me**`

- **teams** contains playing teams. Example contents:

```yaml
teams:
  - ip: 10.70.0.2
    name: Team1
  - ip: 10.70.1.2
    name: "Team2 (highlighted)"
    highlighted: true
```

Highlighted teams will be marked on the scoreboard with a rainbow border.

- **tasks** contains configuration of checkers and task-related parameters. Example:

```yaml
tasks:
  - checker: collacode/checker.py
    checker_type: gevent_pfr
    checker_timeout: 30
    default_score: 1500
    gets: 3
    name: collacode
    places: 1
    puts: 3

  - checker: tiktak/checker.py
    checker_type: hackerdom
    checker_timeout: 30
    gets: 2
    name: tiktak
    places: 3
    puts: 2
``` 

## Checkers

Checksystem is completely compatible with Hackerdom checkers, but some config-level enhancements were added (see below).
Checkers are configured for each task independently. It's recommended to put each checker in a separate folder
under `checkers` in project root. Checker is considered to consist of the main executable and some auxiliary files in
the same folder.

Checker-related configuration variables:

- `checker`: path to the main checker executable (relative to `checkers` folder), which need to be **world-executable**
  (run `chmod o+rx checker_executable`)

- `puts`: number of flags to put for each team for each round

- `gets`: number of flags to check from the last `flag_lifetime` rounds
  (see [Configuration and usage](#configuration-and-usage) for lifetime description).

- `places`: large tasks may contain a lot of possible places for a flag, that is the number. It's randomized for each
  `put` from the range `[1, places]` and passed to the checker's `PUT` and `GET` actions.

- `checker_timeout` (seconds): timeout for **each** checker action. As there're at minumum 3 actions run (depending on
  `puts` and `gets`), it's recommended to set `round_time` at least 4 times greater than the maximum checker timeout if
  possible.

- `checker_type` is an option containing tags, divided by an underscore,
  (missing tags are ignored). Examples: `hackerdom` (hackerdom tag ignored, so no modifier tags are applied),
  `gevent_pfr` (gevent checker with public flag data returned). Currently supported tags:

    - `pfr`: checker returns public flag data (e.g. username of flag user) from `PUT` action as a **public message**,
      private flag data (`flag_id`) as a **private message**, and **public message** is shown
      on `/api/client/attack_data` for participants. If checker does not have this tag, no attack data is shown for the
      task.

    - `nfr`: `flag_id` passed to `PUT` is also passed to `GET` the same flag. That way, `flag_id` is used to seed the
      random generator in checkers so it would return the same values for `GET` and `PUT`. Checkers supporting this
      options are quite rare (and old), so **don't use it** unless you're sure.

    - `gevent`: an experimental checker type to make checkers faster. **Don't use it** if you're not absolutely sure you
      know how it works. **Don't use it** on long and (or) large competitions! Example checker
      is [here](tests/service/checker/gevent_checker.py).

More detailed explanation of checker tags can be
found [in this issue](https://github.com/pomo-mondreganto/ForcAD/issues/18#issuecomment-618072993).

- `env_path`: path or a combination of paths to be prepended to `PATH` env variable (e.g. path to chromedriver). By
  default, `checkers/bin` is used, so all auxiliary executables can be but there.

See more in [checker writing](#writing-a-checker) section.

### Checkers folder

`checkers` folder in project root (containing all checker folders) is recommended to have the following structure:

```yaml
checkers:
  - requirements.txt  <--   automatically installed (with pip) combined requirements of all checkers
  - task1:
      - checker.py  <--   executable
  - task2:
      - checker.py  <--   executable
```

### Writing a checker

See the [corresponding wiki page](https://github.com/pomo-mondreganto/ForcAD/wiki/Writing-a-checker) on how to write a
checker.

## Wiki

More extensive reading can be found in the [wiki pages](https://github.com/pomo-mondreganto/ForcAD/wiki).
