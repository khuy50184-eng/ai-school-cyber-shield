from flask import Flask, request, jsonify, render_template
import math
import re
import os

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
    reasons = []

    domain = re.sub(r'^https?://', '', url).split('/')[0]

    # 1️⃣ Entropy cao (domain random)
    ent = entropy(domain)
    if ent > 3.8:
        score += 25
        reasons.append("Domain có entropy cao (có thể là domain ngẫu nhiên).")

    # 2️⃣ Nhiều số
    digit_count = len(re.findall(r'\d', domain))
    if digit_count > 3:
        score += 15
        reasons.append("Domain chứa nhiều chữ số bất thường.")

    # 3️⃣ Nhiều subdomain
    if domain.count('.') > 2:
        score += 15
        reasons.append("Có nhiều subdomain (có thể che giấu domain chính).")

    # 4️⃣ Từ khóa nguy hiểm
    danger_words = ["login","verify","update","bank","secure","account","confirm","urgent"]
    for word in danger_words:
        if word in url:
            score += 10
            reasons.append(f"Chứa từ khóa đáng ngờ: {word}")

    # 5️⃣ Không HTTPS
    if not url.startswith("https://"):
        score += 15
        reasons.append("Không sử dụng HTTPS.")

    # 6️⃣ Domain là IP
    if re.match(r"^(https?:\/\/)?\d+\.\d+\.\d+\.\d+", url):
        score += 25
        reasons.append("Sử dụng địa chỉ IP thay vì tên miền.")

    if score > 100:
        score = 100

    return score, reasons


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

    data = request.get_json()
    url = data.get("url", "").lower()

    if not url:
        return jsonify({"error": "URL không hợp lệ"}), 400

    score, reasons = analyze_url(url)

    return jsonify({
        "score": score,
        "reasons": reasons
    })


# =========================
# CHẠY SERVER (Render compatible)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
