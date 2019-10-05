import os
import asyncio
from flask import Flask, jsonify, request
from client import reply
from recommend_song import recommend_song

app = Flask(__name__)


@app.route('/fetch/',  methods=['POST'])
def fetch():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        d = {"error": {"message": "Error: Content-Type must be application/json."}}
        return jsonify(d), 400

    data = request.json
    if data.get("id_str") is None or data.get("screen_name") is None:
        d = {"error": {"message": "Error: Invalid parameter."}}
        return jsonify(d), 400

    screen_name = data.get("screen_name")
    id_str = data.get("id_str")

    task(screen_name, id_str)

    d = {"id_str": id_str, "screen_name": screen_name}
    return jsonify(d)

def task(screen_name, id_str):
    song_name, file_name = recommend_song(screen_name, id_str)
    song_name = "hoge"
    message = f"あなたにおすすめの曲は{song_name}です！"
    reply(message, id_str)


@app.route('/parfait/',  methods=['POST'])
def parfait():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        d = {"error": {"message": "Error: Content-Type must be application/json."}}
        return jsonify(d), 400

    data = request.json
    if data.get("id_str") is None or data.get("screen_name") is None:
        d = {"error": {"message": "Error: Invalid parameter."}}
        return jsonify(d), 400

    screen_name = data.get("screen_name")
    id_str = data.get("id_str")

    reply_text = "#パヘ食べたい https://youtu.be/o1e9hdMjUi0"
    reply(reply_text, id_str)

    d = {"id_str": id_str, "screen_name": screen_name}
    return jsonify(d)


def wakati_func(screen_name, in_reply_to_status_id):
    return "あなたのおすすめの曲は From Zero feat. 利香 です！"


@app.route('/')
def health_check():
    d = {"status": "ok"}
    return jsonify(d)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
