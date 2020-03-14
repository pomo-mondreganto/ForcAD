FROM postgres:12.1

RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc make postgresql-server-dev-12 \
    && rm -rf /var/lib/apt/lists/*

ADD backend/fast_rs /rs
RUN make -C /rs