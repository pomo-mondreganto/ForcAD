FROM nginx:1.17.9-alpine

COPY ./docker_config/nginx/conf/ /etc/nginx/conf.d/
COPY ./docker_config/nginx/proxy_params /etc/nginx/proxy_params
COPY ./front/dist /var/www/front

CMD ["nginx", "-g", "daemon off;"]