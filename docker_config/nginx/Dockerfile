FROM nginx:1.15.9-alpine

ADD ./docker_config/nginx/conf/ /etc/nginx/conf.d/
ADD ./docker_config/nginx/proxy_params /etc/nginx/proxy_params
ADD ./front/dist /var/www/front

CMD ["nginx", "-g", "daemon off;"]