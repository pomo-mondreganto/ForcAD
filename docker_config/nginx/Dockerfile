FROM nginx:1.15.12-alpine

ADD ./docker_config/nginx/conf/ /etc/nginx/conf.d/
ADD ./docker_config/nginx/proxy_params /etc/nginx/proxy_params

CMD ["nginx", "-g", "daemon off;"]