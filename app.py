from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "SpendingPartner AI Server is running 🚀"

# ---------------- ANALYZE EXPENSES ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "expenses" not in data:
        return jsonify({"error": "Invalid input"}), 400

    expenses = data["expenses"]
    amounts = np.array([float(e["amount"]) for e in expenses])

    avg = float(np.mean(amounts))
    max_spent = float(np.max(amounts))

    anomaly = max_spent > avg * 1.5

    if anomaly:
        reason = f"Expense ₹{max_spent} is unusually high compared to your average ₹{round(avg,2)}"
    else:
        reason = "Spending is within normal range"

    return jsonify({
        "average_spend": round(avg, 2),
        "highest_spend": round(max_spent, 2),
        "anomaly_detected": anomaly,
        "reason": reason
    })


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

