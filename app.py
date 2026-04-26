from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from analysis_service import (
    analyze_vader,
    analyze_shap,
    analyze_hybrid,
    compare_all,
    get_history,
    get_summary,
    build_csv,
    add_single_history
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Fake Review Detection API running"})

@app.route("/analyze/vader", methods=["POST"])
def analyze_vader_route():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = analyze_vader(text)
    add_single_history(text, result)
    return jsonify(result)

@app.route("/analyze/shap", methods=["POST"])
def analyze_shap_route():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = analyze_shap(text)
    add_single_history(text, result)
    return jsonify(result)

@app.route("/analyze/hybrid", methods=["POST"])
def analyze_hybrid_route():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = analyze_hybrid(text)
    add_single_history(text, result)
    return jsonify(result)

@app.route("/compare", methods=["POST"])
def compare_route():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = compare_all(text)
    return jsonify(result)

@app.route("/history", methods=["GET"])
def history_route():
    return jsonify(get_history())

@app.route("/reports/summary", methods=["GET"])
def reports_summary_route():
    return jsonify(get_summary())

@app.route("/reports/download", methods=["GET"])
def reports_download_route():
    csv_data = build_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis_report.csv"}
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)