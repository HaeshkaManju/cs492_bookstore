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

@app.route("/version")
def version():
    return jsonify({
        "application": "Bookstore Management System",
        "version": "1.0"
    })

if __name__ == "__main__":
    app.run(debug=True)