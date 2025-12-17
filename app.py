from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return "SpendingPartner AI Server is running 🚀"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    expenses = data.get("expenses", [])

    if not expenses:
        return jsonify({"error": "No expense data"}), 400

    amounts = np.array([e["amount"] for e in expenses])

    avg = float(np.mean(amounts))
    max_spent = float(np.max(amounts))

    anomaly = max_spent > avg * 2

    return jsonify({
        "average_spend": round(avg, 2),
        "highest_spend": max_spent,
        "anomaly_detected": anomaly
    })

if __name__ == "__main__":
    app.run(debug=True)
