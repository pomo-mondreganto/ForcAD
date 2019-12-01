FROM node:11.9.0-alpine

RUN mkdir /app
ADD ./frontend/package.json /app/package.json
ADD ./frontend/yarn.lock /app/yarn.lock
WORKDIR /app
RUN yarn install

ADD ./frontend/ /app

ADD ./docker_config/react_builder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR /

CMD ["/entrypoint.sh"]
