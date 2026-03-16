from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow InfinityFree PHP site to call this

# ─── HOME ─────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "SpendingPartner AI v2.0"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# ─── ANALYZE ──────────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    data     = request.get_json()
    expenses = data.get("expenses", [])
    if not expenses:
        return jsonify({"error": "No expenses provided"}), 400

    amounts = np.array([e["amount"] for e in expenses])
    avg     = float(np.mean(amounts))
    max_val = float(np.max(amounts))
    total   = float(np.sum(amounts))
    std_dev = float(np.std(amounts))

    anomaly_items = [expenses[i] for i, a in enumerate(amounts) if a > avg * 2]

    categories = {}
    for e in expenses:
        cat = e.get("category", "General")
        categories[cat] = categories.get(cat, 0) + e["amount"]

    trend = "stable"
    if len(expenses) >= 14:
        recent = float(np.mean(amounts[-7:]))
        prior  = float(np.mean(amounts[-14:-7]))
        if recent > prior * 1.15:   trend = "increasing"
        elif recent < prior * 0.85: trend = "decreasing"

    if std_dev > avg * 0.8:
        insight = "Your spending is highly irregular. Set weekly category limits."
    elif trend == "increasing":
        insight = "Spending is trending UP. Review recent large purchases."
    elif trend == "decreasing":
        insight = "Spending is trending DOWN. Keep it up!"
    elif max_val > avg * 2.5:
        insight = f"One large expense ₹{round(max_val,2)} is pulling up your average."
    else:
        insight = "Spending looks steady. Watch for sudden spikes."

    return jsonify({
        "average_spend":    round(avg, 2),
        "highest_spend":    round(max_val, 2),
        "lowest_spend":     round(float(np.min(amounts)), 2),
        "total_spend":      round(total, 2),
        "std_deviation":    round(std_dev, 2),
        "anomaly_detected": len(anomaly_items) > 0,
        "anomaly_count":    len(anomaly_items),
        "anomaly_items":    anomaly_items,
        "category_totals":  {k: round(v, 2) for k, v in categories.items()},
        "trend":            trend,
        "insight":          insight
    })

# ─── RISK ─────────────────────────────────────────────────────────────────────
@app.route("/risk", methods=["POST"])
def risk():
    data         = request.get_json()
    expenses     = data.get("expenses", [])
    total_budget = data.get("total_budget", 0)

    if len(expenses) < 3 or total_budget <= 0:
        return jsonify({"risk_score": 10, "level": "Low",
                        "reason": "Not enough data yet",
                        "recommendations": ["Add more transactions to get a score."]})

    amounts     = np.array([e["amount"] for e in expenses])
    total_spent = float(np.sum(amounts))
    avg         = float(np.mean(amounts))
    spikes      = int(np.sum(amounts > avg * 1.6))
    spike_score = (spikes / len(amounts)) * 40
    usage_pct   = (total_spent / total_budget) * 100
    burn_score  = min(usage_pct * 0.6, 60)
    risk_score  = int(min(100, spike_score + burn_score))

    if risk_score >= 70:
        level = "High"
        recs  = ["Pause non-essential spending.", "Review largest recent transactions.",
                 "Consider raising your budget."]
    elif risk_score >= 40:
        level = "Medium"
        recs  = ["Monitor daily spend rate.", "Avoid large one-off purchases."]
    else:
        level = "Low"
        recs  = ["You are on track. Keep it up!"]

    return jsonify({
        "risk_score":      risk_score,
        "level":           level,
        "usage_percent":   round(usage_pct, 1),
        "reason":          f"{int(usage_pct)}% of budget used, {spikes} spike transactions",
        "recommendations": recs
    })

# ─── PREDICT ──────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    data     = request.get_json()
    expenses = data.get("expenses", [])
    if len(expenses) < 5:
        return jsonify({"prediction": "Need at least 5 transactions to predict"})

    amounts    = np.array([e["amount"] for e in expenses])
    avg_daily  = float(np.mean(amounts[-7:]))
    next_week  = round(avg_daily * 7, 2)
    next_month = round(avg_daily * 30, 2)
    slope      = float(np.polyfit(np.arange(len(amounts)), amounts, 1)[0])
    trend      = "upward" if slope > 0.5 else "downward" if slope < -0.5 else "flat"

    return jsonify({
        "avg_daily_spend":       round(avg_daily, 2),
        "next_7_days_estimate":  next_week,
        "next_30_days_estimate": next_month,
        "trend_direction":       trend,
        "message":               f"You may spend around ₹{next_week} in the next 7 days"
    })

# ─── BASELINE ─────────────────────────────────────────────────────────────────
@app.route("/baseline/build", methods=["POST"])
def build_baseline():
    data     = request.get_json()
    expenses = data.get("expenses", [])
    if not expenses:
        return jsonify({"error": "No expenses provided"}), 400

    amounts = np.array([e["amount"] for e in expenses])
    daily   = {}
    for e in expenses:
        day = e["created_at"][:10]
        daily[day] = daily.get(day, 0) + e["amount"]

    avg_daily    = float(np.mean(list(daily.values())))
    avg_txn      = float(np.mean(amounts))
    max_normal   = float(np.percentile(amounts, 90))
    freq         = len(amounts) / max(len(daily), 1)
    hours        = [int(e["created_at"][11:13]) for e in expenses]
    normal_hours = [h for h, _ in Counter(hours).most_common(4)]
    ratio        = float(np.std(amounts)) / avg_txn if avg_txn > 0 else 0
    volatility   = "low" if ratio < 0.5 else "medium" if ratio < 1 else "high"

    return jsonify({
        "avg_daily_spend":     round(avg_daily, 2),
        "avg_txn_amount":      round(avg_txn, 2),
        "max_normal_txn":      round(max_normal, 2),
        "daily_txn_frequency": round(freq, 2),
        "normal_hours":        normal_hours,
        "volatility":          volatility
    })

# ─── SECURE RISK ──────────────────────────────────────────────────────────────
@app.route("/secure-risk", methods=["POST"])
def secure_risk():
    data          = request.get_json()
    expenses      = data.get("expenses", [])
    total_budget  = data.get("total_budget", 0)
    identity_risk = data.get("identity_risk", "LOW")

    if len(expenses) < 3 or total_budget <= 0:
        finance_risk, finance_score, usage_pct = "Low", 10, 0
    else:
        amounts       = np.array([e["amount"] for e in expenses])
        total_spent   = float(np.sum(amounts))
        avg           = float(np.mean(amounts))
        spikes        = int(np.sum(amounts > avg * 1.6))
        usage_pct     = (total_spent / total_budget) * 100
        finance_score = int(min(100, (spikes / len(amounts)) * 40 + min(usage_pct * 0.6, 60)))
        finance_risk  = "High" if finance_score >= 70 else "Medium" if finance_score >= 40 else "Low"

    if identity_risk == "HIGH" and finance_risk == "High": action = "BLOCK"
    elif identity_risk == "HIGH":                          action = "VERIFY"
    elif finance_risk == "High":                           action = "WARN"
    else:                                                  action = "ALLOW"

    return jsonify({
        "finance_risk":  finance_risk,
        "finance_score": finance_score,
        "identity_risk": identity_risk,
        "final_action":  action,
        "usage_percent": round(usage_pct, 1),
        "timestamp":     datetime.utcnow().isoformat()
    })

# ─── RUN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
