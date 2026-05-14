from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Bookstore Management System API is running",
        "status": "success"
    })

@app.route("/health")
def health():
    return jsonify({
        "service": "bookstore-api",
        "status": "healthy"
    })

if __name__ == "__main__":
    app.run(debug=True)