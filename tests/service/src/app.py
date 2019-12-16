from flask import Flask, request, jsonify

flags = dict()
app = Flask(__name__)


@app.route('/put/', methods=['POST'])
def put():
    flag_id = request.json['id']
    vuln = request.json['vuln']
    flag = request.json['flag']
    flags[f'{vuln}:{flag_id}'] = flag
    return jsonify({'status': 'ok'})


@app.route('/get/', methods=['GET'])
def get():
    flag_id = request.args['id']
    vuln = request.args['vuln']
    flag = flags[f'{vuln}:{flag_id}']
    return jsonify({'flag': flag})


@app.route('/ping/', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
