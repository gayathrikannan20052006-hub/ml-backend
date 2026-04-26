import re
from datetime import datetime

history_store = []

fake_keywords = [
    "best product ever",
    "changed my life",
    "life changing",
    "must buy",
    "worth every penny",
    "absolutely perfect",
    "five stars",
    "highly recommend",
    "amazing product",
    "excellent product",
    "cannot live without",
]

real_keywords = [
    "delivery",
    "battery",
    "screen",
    "quality",
    "price",
    "material",
    "design",
    "size",
    "performance",
    "packaging",
    "camera",
    "charger",
]

def clean_text(text):
    return text.strip().lower()

def analyze_text_features(text):
    text_lower = clean_text(text)

    fake_score = 0
    real_score = 0
    indicators = []

    for word in fake_keywords:
        if word in text_lower:
            fake_score += 15
            indicators.append(f"Contains suspicious phrase: '{word}'")

    for word in real_keywords:
        if word in text_lower:
            real_score += 8

    if re.search(r"\b([1-5]\s*stars?|five stars?)\b", text_lower):
        fake_score += 15
        indicators.append("Mentions star rating in review text")

    if text.count("!") >= 2:
        fake_score += 10
        indicators.append("Too many exclamation marks")

    word_count = len(text.split())
    if word_count < 8:
        fake_score += 10
        indicators.append("Review is too short")

    if fake_score > 20 and real_score == 0:
        fake_score += 10
        indicators.append("Generic praise without product-specific details")

    return fake_score, real_score, indicators

def analyze_vader(text):
    fake_score, real_score, indicators = analyze_text_features(text)
    confidence = min(100, max(0, 30 + fake_score - real_score))

    if confidence >= 60:
        result = "FAKE"
        certainty = "High" if confidence >= 75 else "Medium"
    else:
        result = "REAL"
        certainty = "Low" if confidence < 45 else "Medium"

    return {
        "method": "VADER",
        "result": result,
        "confidence": confidence,
        "certainty": certainty,
        "indicators": indicators
    }

def analyze_shap(text):
    fake_score, real_score, indicators = analyze_text_features(text)
    confidence = min(100, max(10, 45 + fake_score - real_score))

    if real_score == 0:
        indicators.append("No specific product details detected")

    if confidence >= 60:
        result = "FAKE"
        certainty = "High" if confidence >= 80 else "Medium"
    else:
        result = "REAL"
        certainty = "Low" if confidence < 45 else "Medium"

    return {
        "method": "SHAP",
        "result": result,
        "confidence": confidence,
        "certainty": certainty,
        "indicators": indicators
    }

def analyze_hybrid(text):
    vader = analyze_vader(text)
    shap = analyze_shap(text)

    confidence = round((vader["confidence"] + shap["confidence"]) / 2)

    fake_votes = 0
    if vader["result"] == "FAKE":
        fake_votes += 1
    if shap["result"] == "FAKE":
        fake_votes += 1

    if confidence >= 65:
        result = "FAKE"
        certainty = "High"
    elif confidence >= 50:
        result = "SUSPICIOUS"
        certainty = "Medium"
    else:
        result = "REAL"
        certainty = "Low"

    indicators = [
        f'VADER: {vader["result"]}',
        f'SHAP: {shap["result"]}',
        f"{fake_votes}/2 methods marked as fake"
    ]

    return {
        "method": "HYBRID",
        "result": result,
        "confidence": confidence,
        "certainty": certainty,
        "indicators": indicators,
        "components": {
            "vader": vader,
            "shap": shap
        }
    }

def compare_all(text):
    vader = analyze_vader(text)
    shap = analyze_shap(text)
    hybrid = analyze_hybrid(text)

    item = {
        "id": len(history_store) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "results": {
            "vader": vader,
            "shap": shap,
            "hybrid": hybrid
        }
    }

    history_store.insert(0, item)
    return item

def add_single_history(text, result_data):
    item = {
        "id": len(history_store) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "results": {
            result_data["method"].lower(): result_data
        }
    }
    history_store.insert(0, item)

def get_history():
    return history_store

def get_summary():
    total = len(history_store)
    fake = 0
    real = 0
    suspicious = 0

    for item in history_store:
        for _, result in item["results"].items():
            if result["result"] == "FAKE":
                fake += 1
            elif result["result"] == "REAL":
                real += 1
            elif result["result"] == "SUSPICIOUS":
                suspicious += 1

    return {
        "total_analyzed": total,
        "fake": fake,
        "real": real,
        "suspicious": suspicious
    }

def build_csv():
    lines = ["id,timestamp,method,result,confidence,certainty,text"]

    for item in history_store:
        for _, result in item["results"].items():
            escaped_text = item["text"].replace('"', '""')
            lines.append(
                f'{item["id"]},"{item["timestamp"]}","{result["method"]}","{result["result"]}",{result["confidence"]},"{result["certainty"]}","{escaped_text}"'
            )

    return "\n".join(lines)