FROM nginx:1.19.1-alpine

COPY docker_config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker_config/nginx/http.conf.template /etc/nginx/http.conf.template

COPY docker_config/nginx/proxy_params /etc/nginx/proxy_params
COPY docker_config/nginx/proxy_params_ws /etc/nginx/proxy_params_ws

COPY front/dist /var/www/front

ARG DNS_RESOLVER
ENV DNS_RESOLVER ${DNS_RESOLVER}
RUN envsubst '\${DNS_RESOLVER}' </etc/nginx/http.conf.template >/etc/nginx/http.conf
