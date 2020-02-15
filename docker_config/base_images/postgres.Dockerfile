FROM postgres:12.1

RUN apt-get update && apt-get install -y gcc make postgresql-server-dev-12

ADD backend/fast_rs /rs
WORKDIR /rs
RUN make
WORKDIR /