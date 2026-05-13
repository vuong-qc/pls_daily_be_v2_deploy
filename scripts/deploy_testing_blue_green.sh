#!/usr/bin/env bash
set -euo pipefail

DEPLOY_BASE_DIR="${DEPLOY_BASE_DIR:-/root/backend_daily}"
DAILY_DOMAIN="${DAILY_DOMAIN:-dailytest.api.pls.edu.vn}"
BLUE_PORT="${APP_BLUE_HOST_PORT:-8004}"
GREEN_PORT="${APP_GREEN_HOST_PORT:-8005}"
NGINX_CONF="${NGINX_CONF:-/etc/nginx/conf.d/backend_daily.conf}"
CERT_DIR="${CERT_DIR:-/etc/letsencrypt/live/$DAILY_DOMAIN}"

cd "$DEPLOY_BASE_DIR"
test -f .env

active_port=""
if [ -f "$NGINX_CONF" ]; then
  active_port="$(sed -n 's/.*proxy_pass http:\/\/127\.0\.0\.1:\([0-9][0-9]*\);.*/\1/p' "$NGINX_CONF" | tail -n 1)"
fi

if [ "$active_port" = "$BLUE_PORT" ]; then
  inactive_service="app_green"
  inactive_port="$GREEN_PORT"
else
  inactive_service="app_blue"
  inactive_port="$BLUE_PORT"
fi

echo "Active port: ${active_port:-unknown}"
echo "Deploying inactive slot: $inactive_service on port $inactive_port"

COMPOSE_PROFILES=bluegreen docker compose up -d --build "$inactive_service"

i=0
until curl -fsS --max-time 5 "http://127.0.0.1:$inactive_port/openapi.json" >/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 30 ]; then
    echo "Healthcheck failed for $inactive_service on port $inactive_port"
    docker compose logs --tail 100 "$inactive_service"
    exit 1
  fi
  sleep 2
done

cat > "$NGINX_CONF" <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name $DAILY_DOMAIN;
    client_max_body_size 200m;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name $DAILY_DOMAIN;
    http2 on;
    client_max_body_size 200m;

    ssl_certificate $CERT_DIR/fullchain.pem;
    ssl_certificate_key $CERT_DIR/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:$inactive_port;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
    }
}
NGINX

nginx -t
systemctl reload nginx

for service in app app_blue app_green; do
  if [ "$service" != "$inactive_service" ]; then
    docker compose stop "$service" >/dev/null 2>&1 || true
  fi
done

curl -fsS --max-time 10 "https://$DAILY_DOMAIN/openapi.json" >/dev/null

echo "Daily backend is live on $inactive_service port $inactive_port"
