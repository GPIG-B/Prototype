#!/usr/bin/env python3
import flask
import argparse
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=9999)
    args = parser.parse_args()
    subprocess.run([
        'gunicorn',
        '--bind', f'{args.host}:{args.port}',
        '--timeout', str(5 * 60),
        'sidecar:build_app()',
    ])


def git_pull_and_restart() -> None:
    yield '<h3>DO NOT REFRESH THIS PAGE</h3>'
    yield 'Pulling latest commit...<br>'
    subprocess.run(['git', 'pull', 'origin', 'master'])
    yield 'Rebuilding docker images...<br>'
    subprocess.run(['docker-compose', 'build'])
    try:
        yield 'Stopping old docker containers...<br>'
        subprocess.run(['docker-compose', 'down'])
    except Exception as e:
        yield 'Failed, see logs'
        raise e
    finally:
        yield 'Starting new docker containers...<br>'
        subprocess.run(['docker-compose', 'up', '--detach'])
    yield 'Success<br>'
    yield '<a href="/">Go back</a>'
    return


sidecar_bp = flask.Blueprint('sidecar', __name__)


@sidecar_bp.route('/', methods=['GET'])
def index() -> flask.Response:
    return flask.Response('''
            <h1>GPIG prototype webhook endpoint</h1>
            <form action="/webhook" method="post">
                <button type="submit">Manual push</button>
            </form>
    ''')


@sidecar_bp.route('/webhook', methods=['GET', 'POST'])
def webhook() -> flask.Response:
    return flask.Response(git_pull_and_restart(), 200)


def build_app() -> flask.Flask:
    app = flask.Flask('sidecar')
    app.register_blueprint(sidecar_bp)
    return app


if __name__ == '__main__':
    main()
