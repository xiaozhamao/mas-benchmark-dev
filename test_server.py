from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Hello, this is a local test endpoint!"})

@app.route("/compute")
def compute():
    total = sum(i*i for i in range(10000))
    return jsonify({"result": total})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
