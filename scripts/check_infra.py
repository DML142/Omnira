#!/usr/bin/env python3
"""Exercise real services using isolated credentials, ports and disposable volumes."""
import base64
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    project = 'omnira-check-' + secrets.token_hex(6)
    password = secrets.token_hex(32)
    env = dict(os.environ)
    for key in ('POSTGRES_PASSWORD', 'RABBITMQ_PASSWORD', 'REDIS_PASSWORD',
                'POSTGRES_PORT', 'RABBITMQ_PORT', 'RABBITMQ_MANAGEMENT_PORT', 'REDIS_PORT'):
        env.pop(key, None)
    with tempfile.TemporaryDirectory(prefix='omnira-infra-') as temp:
        env_file = Path(temp) / '.env'
        env_file.write_text('')
        env_file.chmod(0o600)
        compose = ['docker', 'compose', '--project-name', project,
                   '--env-file', str(env_file), '-f', str(ROOT / 'docker-compose.yml')]

        def run(*args, capture=False):
            return subprocess.run([*compose, *args], cwd=ROOT, env=env, check=True,
                                  text=True, stdout=subprocess.PIPE if capture else None,
                                  timeout=300).stdout

        missing = subprocess.run([*compose, 'config', '--quiet'], cwd=ROOT, env=env,
                                 capture_output=True, timeout=30)
        if missing.returncode == 0:
            raise RuntimeError('Missing credentials were accepted')
        env_file.write_text(''.join(f'{key}_PASSWORD={password}\n'
                                   for key in ('POSTGRES', 'RABBITMQ', 'REDIS'))
                            + ''.join(f'{key}_PORT=0\n' for key in
                                      ('POSTGRES', 'RABBITMQ', 'RABBITMQ_MANAGEMENT', 'REDIS')))
        run('config', '--quiet')
        config = json.loads(run('config', '--format', 'json', capture=True))
        for service in config['services'].values():
            if not service.get('healthcheck'):
                raise RuntimeError('Missing healthcheck')
            for port in service['ports']:
                if port['host_ip'] != '127.0.0.1':
                    raise RuntimeError('Infrastructure port exposed beyond loopback')

        def sql(query):
            return run('exec', '-T', 'postgres', 'sh', '-c',
                       'PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U omnira '
                       '-d omnira -v ON_ERROR_STOP=1 -Atc "$1"', 'sh', query,
                       capture=True).strip()

        def redis(*args):
            return run('exec', '-T', 'redis', 'sh', '-c',
                       'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli --no-auth-warning "$@"',
                       'sh', *args, capture=True).strip()

        def rabbit(method, path, payload=None):
            address = run('port', 'rabbitmq', '15672', capture=True).strip()
            auth = base64.b64encode(('omnira:' + password).encode()).decode()
            body = json.dumps(payload).encode() if payload is not None else None
            request = urllib.request.Request('http://' + address + '/api/' + path,
                                             data=body, method=method,
                                             headers={'Authorization': 'Basic ' + auth,
                                                      'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read()
                return json.loads(data) if data else None

        try:
            print('Starting isolated infrastructure with fresh volumes.', flush=True)
            run('up', '-d', '--wait', '--wait-timeout', '180')
            if sql('SELECT 1') != '1' or redis('PING') != 'PONG':
                raise RuntimeError('Authenticated infrastructure probe failed')
            denied = run('exec', '-T', 'redis', 'redis-cli', 'PING', capture=True)
            if 'NOAUTH' not in denied:
                raise RuntimeError('Redis allowed unauthenticated access')
            sql('CREATE TABLE foundation_probe (value text NOT NULL); '
                "INSERT INTO foundation_probe VALUES ('retained')")
            if redis('SET', 'foundation_probe', 'retained') != 'OK':
                raise RuntimeError('Redis write failed')
            rabbit('PUT', 'queues/%2F/foundation-probe',
                   {'durable': True, 'auto_delete': False, 'arguments': {}})
            published = rabbit('POST', 'exchanges/%2F/amq.default/publish', {
                'properties': {'delivery_mode': 2}, 'routing_key': 'foundation-probe',
                'payload': 'retained', 'payload_encoding': 'string'})
            if not published['routed']:
                raise RuntimeError('RabbitMQ message not routed')
            print('Recreating containers; checking persisted data in all three services.', flush=True)
            run('down', '--timeout', '30')
            run('up', '-d', '--wait', '--wait-timeout', '180')
            if sql('SELECT value FROM foundation_probe') != 'retained':
                raise RuntimeError('PostgreSQL data did not survive recreation')
            if redis('GET', 'foundation_probe') != 'retained':
                raise RuntimeError('Redis AOF did not survive recreation')
            messages = rabbit('POST', 'queues/%2F/foundation-probe/get', {
                'count': 1, 'ackmode': 'ack_requeue_false', 'encoding': 'auto'})
            if len(messages) != 1 or messages[0]['payload'] != 'retained':
                raise RuntimeError('RabbitMQ durable message did not survive recreation')
        finally:
            run('down', '--volumes', '--remove-orphans', '--timeout', '30')
        for command in (['ps', '-aq'], ['volume', 'ls', '-q'], ['network', 'ls', '-q']):
            remaining = subprocess.check_output(
                ['docker', *command, '--filter', f'label=com.docker.compose.project={project}'],
                text=True, timeout=30)
            if remaining.strip():
                raise RuntimeError('Test resources remain after teardown')
        print('Infrastructure checks passed: auth, loopback, persistence and clean teardown.')


if __name__ == '__main__':
    main()
