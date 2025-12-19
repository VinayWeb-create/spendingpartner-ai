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
    expenses = data.get("expenses", [])

    amounts = np.array([e["amount"] for e in expenses])

    avg = float(np.mean(amounts))
    max_spent = float(np.max(amounts))

    anomaly = max_spent > avg * 2

    return jsonify({
        "average_spend": round(avg, 2),
        "highest_spend": max_spent,
        "anomaly_detected": anomaly,
        "reason": f"Expense ₹{max_spent} is unusually high compared to your average ₹{round(avg,2)}"
    })


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  


