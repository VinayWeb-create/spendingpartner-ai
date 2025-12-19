from flask import Flask, request, jsonify
import numpy as np
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "SpendingPartner AI Server is running 🚀"

# ---------------- ANALYZE EXPENSES ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "expenses" not in data:
        return jsonify({"error": "Invalid input"}), 400

    expenses = data.get("expenses", [])

    if len(expenses) < 3:
        return jsonify({
            "message": "Not enough data for AI analysis"
        })

    # ----------------------------------
    # PREP DATA
    # ----------------------------------
    amounts = np.array([float(e["amount"]) for e in expenses])
    categories = [e.get("category", "unknown") for e in expenses]
    dates = [e.get("date") for e in expenses]

    total_spent = float(np.sum(amounts))
    avg_spend = float(np.mean(amounts))
    std_spend = float(np.std(amounts))
    latest_amount = float(amounts[-1])

    # ----------------------------------
    # 1️⃣ EXPENSE ANOMALY DETECTION
    # ----------------------------------
    anomaly_detected = latest_amount > (avg_spend + 2 * std_spend)

    anomaly_reason = None
    if anomaly_detected:
        anomaly_reason = (
            f"Expense ₹{latest_amount} is unusually high "
            f"compared to your average ₹{round(avg_spend,2)}"
        )

    # ----------------------------------
    # 2️⃣ FUTURE EXPENSE PREDICTION
    # ----------------------------------
    unique_days = len(set(dates))
    daily_avg = total_spent / max(unique_days, 1)
    next_7_days_prediction = round(daily_avg * 7, 2)

    # ----------------------------------
    # 3️⃣ SMART BUDGET AUTO-GENERATION
    # ----------------------------------
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)

    for e in expenses:
        category_totals[e["category"]] += float(e["amount"])
        category_counts[e["category"]] += 1

    smart_budgets = {}
    for cat in category_totals:
        avg_cat = category_totals[cat] / category_counts[cat]
        smart_budgets[cat] = round(avg_cat * 1.15, 2)  # +15% buffer

    # ----------------------------------
    # 4️⃣ BEHAVIORAL SPENDING RISK SCORE
    # ----------------------------------
    anomaly_penalty = 40 if anomaly_detected else 0
    overspend_penalty = min((latest_amount / (avg_spend + 1)) * 40, 40)
    imbalance_penalty = (
        max(category_totals.values()) / total_spent
    ) * 20

    risk_score = int(100 - (anomaly_penalty + overspend_penalty + imbalance_penalty))
    risk_score = max(0, min(100, risk_score))

    if risk_score >= 80:
        risk_level = "Low"
    elif risk_score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # ----------------------------------
    # 5️⃣ AI INSIGHTS & ALERTS
    # ----------------------------------
    insights = []

    if anomaly_detected:
        insights.append("Unusual expense spike detected")

    if risk_level == "High":
        insights.append("High-risk spending behavior detected")

    hottest_category = max(category_totals, key=category_totals.get)
    insights.append(f"Highest spending category: {hottest_category}")

    # ----------------------------------
    # FINAL RESPONSE (BACKWARD + ADVANCED)
    # ----------------------------------
    return jsonify({
        # 🔹 Old fields (keeps your dashboard safe)
        "average_spend": round(avg_spend, 2),
        "highest_spend": float(np.max(amounts)),
        "anomaly_detected": anomaly_detected,
        "reason": anomaly_reason,

        # 🔹 New AI features
        "future_prediction_7_days": next_7_days_prediction,
        "smart_budgets": smart_budgets,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "insights": insights
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
