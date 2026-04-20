import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot stub is running", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
