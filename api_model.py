import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
MODEL_DIR = 'artifacts_sklearn171'
MODEL_FILE = 'model.joblib'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

# Global variable to hold the model
model = None

def load_model():
    global model
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from {MODEL_PATH}...")
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
        else:
            print(f"Model file not found at {MODEL_PATH}. Using dummy logic.")
    except Exception as e:
        print(f"Error loading model: {e}. Using dummy logic.")

# Load model on startup
load_model()

def get_dummy_prediction(usia, tinggi, berat, gender_code):
    """
    Dummy logic to simulate prediction when model is not available.
    Simple heuristic for demonstration purposes.
    """
    # Very basic WHO-like approximation (NOT ACCURATE MEDICALLY)
    # Average height at 12 months is ~75cm.
    # Average height at 24 months is ~87cm.
    
    # Simple linear expectation: 50cm (birth) + 2cm/month approx
    expected_height = 50 + (usia * 1.5)
    
    if tinggi < (expected_height * 0.85):
        return 0  # Sangat Pendek
    elif tinggi < (expected_height * 0.95):
        return 1  # Pendek
    elif tinggi > (expected_height * 1.15):
        return 3  # Tinggi
    else:
        return 2  # Normal

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['usia_bulan', 'tinggi_badan', 'berat_badan', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        usia = int(data['usia_bulan'])
        tinggi = float(data['tinggi_badan'])
        berat = float(data['berat_badan'])
        gender_input = data['gender'] # Expect 'L'/'P' or 'Laki-laki'/'Perempuan'

        # Preprocessing
        # Map gender to 1 (Laki-laki) or 0 (Perempuan)
        if gender_input.lower() in ['l', 'laki-laki', 'laki']:
            gender_val = 1
            gender_str = 'Laki-laki'
        else:
            gender_val = 0
            gender_str = 'Perempuan'

        # Prepare data for model (matching the training columns)
        # Columns: 'Umur (bulan)', 'Tinggi Badan (cm)', 'Berat Badan (kg)', 'Jenis Kelamin', 'Wasting'
        # Note: 'Wasting' seems to be required by the model. We'll initialize it to 0 (Normal) as a placeholder
        # since we don't have a separate Wasting model yet.
        input_data = pd.DataFrame([{
            'Umur (bulan)': usia,
            'Tinggi Badan (cm)': tinggi,
            'Berat Badan (kg)': berat,
            'Jenis Kelamin': gender_val,
            'Wasting': "Normal weight" 
        }])

        # Prediction Logic
        prediction_class = None
        confidence = "N/A"
        message = ""

        if model:
            try:
                # TODO: LOAD PICKLE MODEL HERE - Already implemented in load_model()
                prediction_class = model.predict(input_data)[0]
                # Try to get probability if supported
                if hasattr(model, 'predict_proba'):
                    probs = model.predict_proba(input_data)[0]
                    # If binary, probs is [prob_0, prob_1]
                    # If prediction is 0, confidence is probs[0]
                    # If prediction is 1, confidence is probs[1]
                    confidence_val = probs[prediction_class]
                    confidence = f"{confidence_val*100:.1f}%"
                else:
                    confidence = "High (Model)"
                message = "Prediction based on AI Model."
            except Exception as e:
                print(f"Prediction error: {e}")
                # Fallback to dummy if model fails during predict
                prediction_class = get_dummy_prediction(usia, tinggi, berat, gender_val)
                message = f"Model error, using fallback logic. Error: {str(e)}"
                confidence = "Low (Fallback)"
        else:
            # Use Dummy Logic
            prediction_class = get_dummy_prediction(usia, tinggi, berat, gender_val)
            message = "Model file not found. Using rule-based fallback logic."
            confidence = "Medium (Rule-based)"

        # Map output class to string
        # Model is Binary: 0 = Normal/Tall, 1 = Stunting (Pendek/Sangat Pendek)
        # Dummy logic returns 0, 1, 2, 3. We need to handle both.
        
        status_text = "Unknown"
        
        if model and message == "Prediction based on AI Model.":
            # Binary Model Mapping
            if prediction_class == 0:
                status_text = "Normal" # Includes Tall
            elif prediction_class == 1:
                status_text = "Stunting" # Includes Severely Stunted
        else:
            # Dummy Logic Mapping (0-3)
            status_map = {
                0: 'Sangat Pendek',
                1: 'Pendek',
                2: 'Normal',
                3: 'Tinggi'
            }
            status_text = status_map.get(prediction_class, "Unknown")

        return jsonify({
            'status': status_text,
            'confidence': confidence,
            'message': message,
            'input_received': {
                'usia': usia,
                'tinggi': tinggi,
                'berat': berat,
                'gender': gender_str
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask Server on port 5000...")
    app.run(debug=True, port=5000)
