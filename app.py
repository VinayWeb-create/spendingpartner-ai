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

# ---------------- RISK SCORE ----------------
@app.route("/risk", methods=["POST"])
def risk():
    data = request.get_json()
    expenses = data.get("expenses", [])

    if len(expenses) < 3:
        return jsonify({
            "risk_score": 10,
            "level": "Low",
            "reason": "Not enough data yet"
        })

    amounts = np.array([e["amount"] for e in expenses])
    avg = np.mean(amounts)
    spikes = np.sum(amounts > avg * 1.8)

    risk_score = min(100, int((spikes / len(amounts)) * 100 + avg / 10))

    level = "Low"
    if risk_score >= 70:
        level = "High"
    elif risk_score >= 40:
        level = "Medium"

    return jsonify({
        "risk_score": risk_score,
        "level": level,
        "reason": f"{spikes} abnormal expenses detected"
    })


# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    expenses = data.get("expenses", [])

    if len(expenses) < 5:
        return jsonify({
            "prediction": "Not enough data to predict"
        })

    amounts = np.array([e["amount"] for e in expenses])
    avg_daily = np.mean(amounts[-7:])

    next_week = round(avg_daily * 7, 2)

    return jsonify({
        "avg_daily_spend": round(avg_daily, 2),
        "next_7_days_estimate": next_week,
        "message": f"You may spend around ₹{next_week} in the next 7 days"
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  



