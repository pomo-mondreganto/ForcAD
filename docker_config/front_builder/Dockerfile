FROM node:11.9.0-alpine

RUN mkdir /app
ADD ./front/package.json /app/package.json
ADD ./front/yarn.lock /app/yarn.lock
WORKDIR /app
RUN yarn install

ADD ./front/ /app

ADD ./docker_config/front_builder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR /

CMD ["/entrypoint.sh"]
