#!/usr/bin/env bash
set -euo pipefail

PROD_SERVER_DEPLOY_DIR="${PROD_SERVER_DEPLOY_DIR:?PROD_SERVER_DEPLOY_DIR is required}"
PROD_NGINX_CONF_PATH="${PROD_NGINX_CONF_PATH:?PROD_NGINX_CONF_PATH is required}"
PROD_APP_BLUE_HOST_PORT="${PROD_APP_BLUE_HOST_PORT:?PROD_APP_BLUE_HOST_PORT is required}"
PROD_APP_GREEN_HOST_PORT="${PROD_APP_GREEN_HOST_PORT:?PROD_APP_GREEN_HOST_PORT is required}"
PROD_PUBLIC_HEALTHCHECK_URL="${PROD_PUBLIC_HEALTHCHECK_URL:?PROD_PUBLIC_HEALTHCHECK_URL is required}"
PROD_PUBLIC_DOCS_URL="${PROD_PUBLIC_DOCS_URL:?PROD_PUBLIC_DOCS_URL is required}"
PROD_PUBLIC_HTTP_HEALTHCHECK_URL="${PROD_PUBLIC_HTTP_HEALTHCHECK_URL:?PROD_PUBLIC_HTTP_HEALTHCHECK_URL is required}"
PROD_PUBLIC_HTTP_DOCS_URL="${PROD_PUBLIC_HTTP_DOCS_URL:?PROD_PUBLIC_HTTP_DOCS_URL is required}"
PROD_COMPOSE_PROJECT_NAME="${PROD_COMPOSE_PROJECT_NAME:?PROD_COMPOSE_PROJECT_NAME is required}"
PROD_DOMAIN="${PROD_DOMAIN:?PROD_DOMAIN is required}"
APP_IMAGE="${APP_IMAGE:-backend-daily-production:local}"
PROD_EXPECTED_PUBLIC_IP="${PROD_EXPECTED_PUBLIC_IP:-}"
HEALTHCHECK_PATH="${HEALTHCHECK_PATH:-/support/check-server}"
MIN_FREE_DISK_MB="${MIN_FREE_DISK_MB:-2048}"

https_nginx_source="${PROD_SERVER_DEPLOY_DIR}/backend_daily.production.conf"
bootstrap_nginx_source="${PROD_SERVER_DEPLOY_DIR}/backend_daily.production.bootstrap.conf"
active_color_file="${PROD_SERVER_DEPLOY_DIR}/.active_color"
app_blue_host_port="${PROD_APP_BLUE_HOST_PORT}"
app_green_host_port="${PROD_APP_GREEN_HOST_PORT}"

if [ -n "$PROD_EXPECTED_PUBLIC_IP" ]; then
  server_public_ip="$(curl -4 --silent --show-error ifconfig.me || true)"
  if [ -z "$server_public_ip" ] || [ "$server_public_ip" != "$PROD_EXPECTED_PUBLIC_IP" ]; then
    echo "Refusing to deploy production stack to unexpected server" >&2
    echo "Expected production public IP: ${PROD_EXPECTED_PUBLIC_IP}" >&2
    echo "Actual remote public IP: ${server_public_ip:-unknown}" >&2
    exit 1
  fi
fi

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
  docker_root="$(sudo docker info --format '{{.DockerRootDir}}' 2>/dev/null || true)"
  if [ -z "$docker_root" ]; then
    docker_root="/var/lib/docker"
  fi

  check_free_disk "$PROD_SERVER_DEPLOY_DIR" "$MIN_FREE_DISK_MB" "Deploy directory"
  if [ -d "$docker_root" ]; then
    check_free_disk "$docker_root" "$MIN_FREE_DISK_MB" "Docker root"
  fi
}

cd "${PROD_SERVER_DEPLOY_DIR}"

if sudo docker compose version >/dev/null 2>&1; then
  compose() {
    sudo --preserve-env=APP_IMAGE docker compose "$@"
  }
  compose_bg() {
    COMPOSE_PROFILES=bluegreen sudo --preserve-env=APP_IMAGE,COMPOSE_PROFILES docker compose "$@"
  }
else
  compose() {
    sudo --preserve-env=APP_IMAGE docker-compose "$@"
  }
  compose_bg() {
    COMPOSE_PROFILES=bluegreen sudo --preserve-env=APP_IMAGE,COMPOSE_PROFILES docker-compose "$@"
  }
fi

wait_for_service_state() {
  service="$1"
  timeout_seconds="$2"
  interval_seconds=2
  elapsed=0

  while [ "$elapsed" -lt "$timeout_seconds" ]; do
    container_id="$(compose ps -q "$service" 2>/dev/null || true)"
    if [ -n "$container_id" ]; then
      status="$(sudo docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null || true)"
      case "$status" in
        healthy|running)
          echo "Service ${service} is ${status}"
          return 0
          ;;
        unhealthy|exited|dead)
          echo "Service ${service} entered unhealthy state: ${status}" >&2
          compose ps || true
          compose logs "$service" --tail 100 || true
          return 1
          ;;
      esac
    fi

    sleep "$interval_seconds"
    elapsed=$((elapsed + interval_seconds))
  done

  echo "Timed out waiting for service ${service}" >&2
  compose ps || true
  compose logs "$service" --tail 100 || true
  return 1
}

wait_for_local_http() {
  url="$1"
  timeout_seconds="$2"
  interval_seconds=2
  elapsed=0

  while [ "$elapsed" -lt "$timeout_seconds" ]; do
    if curl --fail --silent --show-error "$url" >/dev/null 2>&1; then
      curl --fail --silent --show-error "$url"
      return 0
    fi

    sleep "$interval_seconds"
    elapsed=$((elapsed + interval_seconds))
  done

  echo "Timed out waiting for local endpoint $url" >&2
  return 1
}

current_backend_port() {
  if [ -f "${PROD_NGINX_CONF_PATH}" ]; then
    grep -oE '127\.0\.0\.1:[0-9]+' "${PROD_NGINX_CONF_PATH}" | head -n 1 | cut -d: -f2
  fi
}

render_nginx_config() {
  source_conf="$1"
  target_port="$2"
  rendered_conf="$(mktemp)"
  sed -e "s|__APP_HOST_PORT__|${target_port}|g" "$source_conf" > "$rendered_conf"
  printf '%s\n' "$rendered_conf"
}

install_production_nginx() {
  target_port="$1"
  nginx_test_log="$(mktemp)"
  rendered_https_conf="$(render_nginx_config "$https_nginx_source" "$target_port")"
  rendered_bootstrap_conf=""

  sudo install -m 644 "$rendered_https_conf" "${PROD_NGINX_CONF_PATH}"
  if sudo nginx -t >"$nginx_test_log" 2>&1; then
    cat "$nginx_test_log"
    nginx_mode="https"
  else
    cat "$nginx_test_log"
    rendered_bootstrap_conf="$(render_nginx_config "$bootstrap_nginx_source" "$target_port")"
    sudo install -m 644 "$rendered_bootstrap_conf" "${PROD_NGINX_CONF_PATH}"
    sudo nginx -t
    nginx_mode="http"
  fi

  rm -f "$nginx_test_log" "$rendered_https_conf"
  if [ -n "$rendered_bootstrap_conf" ]; then
    rm -f "$rendered_bootstrap_conf"
  fi

  sudo systemctl reload nginx
}

current_backend_port="$(current_backend_port || true)"
active_color=""
case "$current_backend_port" in
  "$app_blue_host_port")
    active_color="blue"
    ;;
  "$app_green_host_port")
    active_color="green"
    ;;
esac
if [ -z "$active_color" ] && [ -f "$active_color_file" ]; then
  active_color="$(tr -d '[:space:]' < "$active_color_file")"
fi
if [ -z "$active_color" ]; then
  active_color="legacy"
fi

if [ "$active_color" = "blue" ]; then
  target_color="green"
  target_port="$app_green_host_port"
  target_service="app_green"
else
  target_color="blue"
  target_port="$app_blue_host_port"
  target_service="app_blue"
  if [ "$active_color" = "legacy" ]; then
    target_color="green"
    target_port="$app_green_host_port"
    target_service="app_green"
  fi
fi

echo "Current active color: ${active_color}"
echo "Target color: ${target_color}"
echo "Target service: ${target_service}"
echo "Target port: ${target_port}"

export APP_IMAGE
check_build_disk
compose up -d mongodb
wait_for_service_state mongodb 90
compose_bg up -d --build --no-deps --force-recreate "$target_service"

if ! wait_for_local_http "http://127.0.0.1:${target_port}${HEALTHCHECK_PATH}" 90; then
  echo "Production app did not become ready on port ${target_port}" >&2
  compose ps || true
  compose_bg ps || true
  compose_bg logs "$target_service" --tail 200 || true
  compose logs mongodb --tail 100 || true
  exit 1
fi

install_production_nginx "$target_port"

if [ "$nginx_mode" = "https" ]; then
  public_healthcheck_url="$PROD_PUBLIC_HEALTHCHECK_URL"
  public_docs_url="$PROD_PUBLIC_DOCS_URL"
else
  public_healthcheck_url="$PROD_PUBLIC_HTTP_HEALTHCHECK_URL"
  public_docs_url="$PROD_PUBLIC_HTTP_DOCS_URL"
fi

if ! curl --fail --silent --show-error --retry 10 --retry-delay 2 "$public_healthcheck_url"; then
  echo "Public healthcheck failed after switching traffic to port ${target_port}" >&2
  if [ -n "$current_backend_port" ] && [ "$current_backend_port" != "$target_port" ]; then
    install_production_nginx "$current_backend_port"
  fi
  exit 1
fi

if ! curl --fail --silent --show-error --retry 10 --retry-delay 2 --head "$public_docs_url"; then
  echo "Public docs check failed after switching traffic to port ${target_port}" >&2
  if [ -n "$current_backend_port" ] && [ "$current_backend_port" != "$target_port" ]; then
    install_production_nginx "$current_backend_port"
  fi
  exit 1
fi

printf '%s\n' "$target_color" > "$active_color_file"

legacy_app_container="$(compose ps -q app 2>/dev/null || true)"
if [ -n "$legacy_app_container" ]; then
  compose rm -sf app || sudo docker rm -f "${PROD_COMPOSE_PROJECT_NAME}-app-1" >/dev/null 2>&1 || true
fi

for service in app_blue app_green; do
  if [ "$service" != "$target_service" ]; then
    compose_bg stop "$service" >/dev/null 2>&1 || true
  fi
done
