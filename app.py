from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={
    r"/disease-info": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure Gemini API key (use environment variables in production)
API_KEY = "AIzaSyB6fMl4E7AgBGvDgGzIaahjSBEwPR3Ynqk"
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

@app.route("/")
def home():
    return "✅ Gemini Disease API is running!"

@app.route("/disease-info", methods=["GET", "POST"])
def disease_info():
    if request.method == "GET":
        return jsonify({
            "message": "Please use POST method with 'disease' parameter",
            "example": {"disease": "diabetes"}
        }), 200

    # Handle POST request
    data = request.get_json()
    if not data or "disease" not in data:
        return jsonify({"error": "Missing 'disease' parameter"}), 400

    disease = data["disease"].strip()
    if not disease:
        return jsonify({"error": "Disease name cannot be empty"}), 400

    prompt = f"""Provide detailed information about {disease} in this exact format:

    **Medication:**
    - [List medications]
    - [Dosage information]
    
    **Food Recommendations:**
    - [Foods to eat]
    - [Foods to avoid]
    
    **Precautions:**
    - [Important precautions]
    - [Lifestyle changes]"""

    try:
        response = model.generate_content(
            prompt,
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )

        result_text = response.text

        # Parse the response
        sections = {
            "medication": [],
            "food": [],
            "precautions": []
        }
        current_section = None
        
        for line in result_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if "medication:" in line.lower():
                current_section = "medication"
            elif "food" in line.lower():
                current_section = "food"
            elif "precaution:" in line.lower():
                current_section = "precautions"
            elif current_section:
                sections[current_section].append(line)

        return jsonify({
            "disease": disease,
            "medication": "\n".join(sections["medication"]) or "No medication information available",
            "food": "\n".join(sections["food"]) or "No dietary information available",
            "precautions": "\n".join(sections["precautions"]) or "No precaution information available"
        })

    except Exception as e:
        return jsonify({
            "error": "Failed to process request",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)