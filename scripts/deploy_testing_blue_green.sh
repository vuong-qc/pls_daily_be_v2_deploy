#!/usr/bin/env bash
set -euo pipefail

DEPLOY_BASE_DIR="${DEPLOY_BASE_DIR:-/root/backend_daily}"
DAILY_DOMAIN="${DAILY_DOMAIN:-dailytestapi.pls.edu.vn}"
BLUE_PORT="${APP_BLUE_HOST_PORT:-8004}"
GREEN_PORT="${APP_GREEN_HOST_PORT:-8005}"
NGINX_CONF="${NGINX_CONF:-/etc/nginx/conf.d/backend_daily.conf}"
CERT_DIR="${CERT_DIR:-/etc/letsencrypt/live/$DAILY_DOMAIN}"
HTTPS_NGINX_TEMPLATE="${HTTPS_NGINX_TEMPLATE:-$DEPLOY_BASE_DIR/deploy/nginx/backend_daily.testing.conf}"
BOOTSTRAP_NGINX_TEMPLATE="${BOOTSTRAP_NGINX_TEMPLATE:-$DEPLOY_BASE_DIR/deploy/nginx/backend_daily.testing.bootstrap.conf}"
MIN_FREE_DISK_MB="${MIN_FREE_DISK_MB:-2048}"

cd "$DEPLOY_BASE_DIR"
test -f .env

check_free_disk() {
  path="$1"
  min_mb="$2"
  label="$3"
  available_mb="$(df -Pm "$path" | awk 'NR == 2 {print $4}')"

  if [ -z "$available_mb" ]; then
    echo "Could not determine free disk for ${label}: ${path}" >&2
    exit 1
  fi

  if [ "$available_mb" -lt "$min_mb" ]; then
    echo "${label} has ${available_mb}MB free; requires at least ${min_mb}MB before build." >&2
    exit 1
  fi

  echo "${label} free disk: ${available_mb}MB"
}

check_build_disk() {
  docker_root="$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || true)"
  if [ -z "$docker_root" ]; then
    docker_root="/var/lib/docker"
  fi

  check_free_disk "$DEPLOY_BASE_DIR" "$MIN_FREE_DISK_MB" "Deploy directory"
  if [ -d "$docker_root" ]; then
    check_free_disk "$docker_root" "$MIN_FREE_DISK_MB" "Docker root"
  fi
}

render_nginx_config() {
  source_conf="$1"
  target_port="$2"
  rendered_conf="$(mktemp)"
  sed \
    -e "s|__DAILY_DOMAIN__|${DAILY_DOMAIN}|g" \
    -e "s|__CERT_DIR__|${CERT_DIR}|g" \
    -e "s|__APP_HOST_PORT__|${target_port}|g" \
    "$source_conf" > "$rendered_conf"
  printf '%s\n' "$rendered_conf"
}

install_testing_nginx() {
  target_port="$1"
  nginx_test_log="$(mktemp)"
  rendered_https_conf="$(render_nginx_config "$HTTPS_NGINX_TEMPLATE" "$target_port")"
  rendered_bootstrap_conf=""

  install -m 644 "$rendered_https_conf" "$NGINX_CONF"
  if nginx -t >"$nginx_test_log" 2>&1; then
    cat "$nginx_test_log"
    nginx_mode="https"
  else
    cat "$nginx_test_log"
    rendered_bootstrap_conf="$(render_nginx_config "$BOOTSTRAP_NGINX_TEMPLATE" "$target_port")"
    install -m 644 "$rendered_bootstrap_conf" "$NGINX_CONF"
    nginx -t
    nginx_mode="http"
  fi

  rm -f "$nginx_test_log" "$rendered_https_conf"
  if [ -n "$rendered_bootstrap_conf" ]; then
    rm -f "$rendered_bootstrap_conf"
  fi

  systemctl reload nginx
}

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

check_build_disk
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

install_testing_nginx "$inactive_port"

for service in app app_blue app_green; do
  if [ "$service" != "$inactive_service" ]; then
    docker compose stop "$service" >/dev/null 2>&1 || true
  fi
done

if [ "$nginx_mode" = "https" ]; then
  curl -fsS --max-time 10 "https://$DAILY_DOMAIN/openapi.json" >/dev/null
else
  curl -fsS --max-time 10 "http://$DAILY_DOMAIN/openapi.json" >/dev/null
fi

echo "Daily backend is live on $inactive_service port $inactive_port"
