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
    total_budget = data.get("total_budget", 0)

    if len(expenses) < 3 or total_budget <= 0:
        return jsonify({
            "risk_score": 10,
            "level": "Low",
            "reason": "Not enough data yet"
        })

    amounts = np.array([e["amount"] for e in expenses])

    total_spent = np.sum(amounts)
    avg = np.mean(amounts)

    # 1️⃣ Spike risk
    spikes = np.sum(amounts > avg * 1.6)
    spike_score = (spikes / len(amounts)) * 40   # max 40

    # 2️⃣ Burn risk (budget usage)
    usage_percent = (total_spent / total_budget) * 100
    burn_score = min(usage_percent * 0.6, 60)    # max 60

    risk_score = int(min(100, spike_score + burn_score))

    if risk_score >= 70:
        level = "High"
    elif risk_score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return jsonify({
        "risk_score": risk_score,
        "level": level,
        "reason": f"{int(usage_percent)}% of budget used, {spikes} abnormal spends detected"
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




