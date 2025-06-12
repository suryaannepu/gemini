from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API key (ensure it's stored securely in production)
API_KEY = "AIzaSyB6fMl4E7AgBGvDgGzIaahjSBEwPR3Ynqk"
genai.configure(api_key=API_KEY)

# Load the correct Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

@app.route("/")
def home():
    return "✅ Gemini Disease API is running!"

@app.route("/disease-info", methods=["POST"])
def disease_info():
    data = request.get_json()
    if not data or "disease" not in data:
        return jsonify({"error": "Missing 'disease' parameter"}), 400

    disease = data["disease"]
    prompt = f"Give the medication, food, and precautions for {disease} in detailed bullet points."

    try:
        response = model.generate_content(prompt)
        result_text = response.text

        # Extract sections manually from the result
        medication = []
        food = []
        precautions = []

        for line in result_text.split("\n"):
            lower = line.lower()
            if "medication" in lower:
                medication.append(line)
            elif "food" in lower:
                food.append(line)
            elif "precaution" in lower:
                precautions.append(line)

        return jsonify({
            "medication": "\n".join(medication) or "Not available.",
            "food": "\n".join(food) or "Not available.",
            "precautions": "\n".join(precautions) or "Not available."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
