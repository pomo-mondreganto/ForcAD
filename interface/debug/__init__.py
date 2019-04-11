import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, make_response
import storage
import json

app = Flask(__name__)


def get_response(status_code, data=None, error=None):
    if error:
        return make_response({'error': error}, status_code)

    return make_response(json.dumps(data), status_code)


@app.route('/status')
def status():
    return 'OK'


@app.route('/')
def main_page():
    round = storage.game.get_current_round()
    team_tasks = storage.tasks.get_teamtasks(round)
    return render_template('index.html', team_tasks=team_tasks)


if __name__ == '__main__':
    app.run(port='5001', debug=True)
