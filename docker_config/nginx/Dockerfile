FROM nginx:1.19.1-alpine

COPY docker_config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker_config/nginx/http.conf /etc/nginx/http.conf
COPY docker_config/nginx/tcp.conf /etc/nginx/tcp.conf

COPY docker_config/nginx/proxy_params /etc/nginx/proxy_params
COPY docker_config/nginx/proxy_params_ws /etc/nginx/proxy_params_ws

COPY front/dist /var/www/front
