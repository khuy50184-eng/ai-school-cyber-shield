from flask import Flask, request, jsonify, render_template
import math
import re

app = Flask(__name__)

# =========================
# TÍNH ENTROPY
# =========================
def entropy(domain):
    if len(domain) == 0:
        return 0
    prob = [float(domain.count(c)) / len(domain) for c in dict.fromkeys(list(domain))]
    return - sum([p * math.log(p) / math.log(2.0) for p in prob])

# =========================
# PHÂN TÍCH URL
# =========================
def analyze_url(url):
    score = 0

    domain = re.sub(r'^https?://', '', url).split('/')[0]

    # entropy cao (domain random)
    if entropy(domain) > 3.8:
        score += 25

    # nhiều số
    if len(re.findall(r'\d', domain)) > 3:
        score += 15

    # nhiều subdomain
    if domain.count('.') > 2:
        score += 15

    # từ khóa nguy hiểm
    danger_words = ["login","verify","update","bank","secure","account"]
    for word in danger_words:
        if word in url:
            score += 10

    # không https
    if not url.startswith("https://"):
        score += 10

    if score > 100:
        score = 100

    return score

# =========================
# ROUTE TRANG CHỦ
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# API PHÂN TÍCH
# =========================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data["url"].lower()

    score = analyze_url(url)

    # Tính % an toàn (đảo ngược score nguy hiểm)
    safe_percent = 100 - score

    if score < 30:
        status = "An toàn"
    elif score < 60:
        status = "Cần xem xét"
    else:
        status = "Nguy hiểm"

    return jsonify({
        "score": score,
        "safe_percent": safe_percent,
        "status": status
    })

if __name__ == "__main__":
    app.run(debug=True)