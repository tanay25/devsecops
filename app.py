from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Flask DevSecOps Application",
        "status": "Running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/about")
def about():
    return jsonify({
        "application": "Flask",
        "version": "1.0"
    })

if __name__ == "__main__":
    app.run(debug=False)
