#!/bin/sh
set -eu
# Hex credentials keep the generated Redis configuration unambiguous.
case "${REDIS_PASSWORD:-}" in
  ''|*[!a-fA-F0-9]*) echo 'REDIS_PASSWORD must be hexadecimal.' >&2; exit 1 ;;
esac
if [ "${#REDIS_PASSWORD}" -lt 32 ]; then
  echo 'REDIS_PASSWORD must contain at least 32 hexadecimal characters.' >&2
  exit 1
fi
umask 077
config=$(mktemp /tmp/omnira-redis.XXXXXX)
printf 'bind 0.0.0.0\nprotected-mode yes\nappendonly yes\ndir /data\nrequirepass %s\n' "$REDIS_PASSWORD" > "$config"
chown redis:redis "$config"
exec /usr/local/bin/docker-entrypoint.sh redis-server "$config"
