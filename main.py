import os
from flask import Flask, jsonify, request
from client import reply

app = Flask(__name__)


@app.route('/fetch/',  methods=['POST'])
def fetch():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        d = {"error": {"message": "Error: Content-Type must be application/json."}}
        return jsonify(d), 400

    data = request.json
    if data.get("id") is None or data.get("screen_name") is None:
        d = {"error": {"message": "Error: Invalid parameter."}}
        return jsonify(d), 400

    screen_name = data.get("screen_name")
    id_ = data.get("id")

    # screen_nameを使った関数とかに渡す
    text = wakati_func(screen_name, id_)

    reply(text, id_)

    d = {"id": id_, "screen_name": screen_name}
    return jsonify(d)


def wakati_func(screen_name, in_reply_to_status_id):
    return "あなたのおすすめの曲は From Zero feat. 利香 です！"


@app.route('/')
def health_check():
    d = {"status": "ok"}
    return jsonify(d)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
