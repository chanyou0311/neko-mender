from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/fetch/',  methods=['POST'])
def fetch():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        d = {"error": {"message": "Error: Content-Type must be application/json."}}
        return jsonify(d), 400

    data = request.json
    if data.get("screen_name") is None:
        d = {"error": {"message": "Error: Invalid parameter."}}
        return jsonify(d), 400

    screen_name = data.get("screen_name")

    # screen_nameを使った関数とかに渡す
    # wakati_func(screen_name)

    d = {"screen_name": screen_name}
    return jsonify(d)

@app.route('/')
def health_check():
    d = {"status": "ok"}
    return jsonify(d)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
