from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global state
sensor_data = []
current_index = 0

CROP_THRESHOLDS = {
    'Tomatoes': {'min': 35, 'optimal_min': 45, 'optimal_max': 65, 'max': 75},
    'Onions': {'min': 30, 'optimal_min': 40, 'optimal_max': 55, 'max': 70},
    'Mint': {'min': 40, 'optimal_min': 50, 'optimal_max': 70, 'max': 80}
}

def load_sensor_data():
    """Load sensor data from CSV file"""
    global sensor_data
    csv_file = os.path.join(os.path.dirname(__file__), 'sensor_data.csv')
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            sensor_data = list(reader)
        print(f"[v0] Loaded {len(sensor_data)} sensor readings from CSV")
        return True
    except Exception as e:
        print(f"[v0] Error loading CSV: {e}")
        return False

def get_recommendation(moisture, crop_type='Tomatoes'):
    """Generate watering recommendation based on soil moisture and crop type"""
    thresholds = CROP_THRESHOLDS.get(crop_type, CROP_THRESHOLDS['Tomatoes'])
    
    if moisture < thresholds['min']:
        return {
            "status": "URGENT - WATER NOW!",
            "urgency": "critical",
            "reason": f"Soil is critically dry for {crop_type}. Immediate watering needed!"
        }
    elif moisture < thresholds['optimal_min']:
        return {
            "status": "WATER SOON",
            "urgency": "high",
            "reason": f"Soil is dry for {crop_type}. Water in the next 2-3 hours."
        }
    elif moisture < thresholds['optimal_max']:
        return {
            "status": "PERFECT - KEEP MONITORING",
            "urgency": "low",
            "reason": f"Soil moisture is optimal for {crop_type}. Excellent conditions!"
        }
    elif moisture < thresholds['max']:
        return {
            "status": "YOU CAN WAIT",
            "urgency": "low",
            "reason": f"Soil has plenty of water for {crop_type}. Monitor in 6-8 hours."
        }
    else:
        return {
            "status": "TOO WET - ENSURE DRAINAGE",
            "urgency": "medium",
            "reason": f"Soil is too wet for {crop_type}. Risk of root rot. Check drainage."
        }

@app.route('/api/sensor/current', methods=['GET'])
def get_current_sensor():
    """Get current sensor reading from dataset for a specific field"""
    global current_index
    
    field_id = request.args.get('field_id', '1')  # Default to field 1
    
    if not sensor_data:
        return jsonify({"error": "No sensor data loaded"}), 500
    
    field_readings = [r for r in sensor_data if r['field_id'] == field_id]
    
    if not field_readings:
        return jsonify({"error": f"No data for field {field_id}"}), 404
    
    reading = field_readings[current_index % len(field_readings)]
    
    moisture = float(reading['soil_moisture'])
    crop_type = reading['crop_type']
    recommendation = get_recommendation(moisture, crop_type)
    
    return jsonify({
        "timestamp": reading['timestamp'],
        "field_id": reading['field_id'],
        "field_name": reading['field_name'],
        "crop_type": crop_type,
        "soil_moisture": moisture,
        "temperature": float(reading['temperature']),
        "humidity": float(reading['humidity']),
        "ph_level": float(reading['ph_level']),
        "recommendation": recommendation,
        "data_point": f"{(current_index % len(field_readings)) + 1}/{len(field_readings)}"
    })

@app.route('/api/sensor/field/<field_id>', methods=['GET'])
def get_field_data(field_id):
    """Get all readings for a specific field"""
    field_readings = [r for r in sensor_data if r['field_id'] == field_id]
    
    if not field_readings:
        return jsonify({"error": f"No data for field {field_id}"}), 404
    
    return jsonify({
        "field_id": field_id,
        "field_name": field_readings[0]['field_name'],
        "crop_type": field_readings[0]['crop_type'],
        "total_readings": len(field_readings),
        "readings": [
            {
                "timestamp": r['timestamp'],
                "soil_moisture": float(r['soil_moisture']),
                "temperature": float(r['temperature']),
                "humidity": float(r['humidity']),
                "ph_level": float(r['ph_level'])
            }
            for r in field_readings
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "data_loaded": len(sensor_data) > 0,
        "total_readings": len(sensor_data)
    })

if __name__ == '__main__':
    if load_sensor_data():
        print("[v0] Starting Flask server...")
        app.run(debug=True, host='localhost', port=5000)
    else:
        print("[v0] Failed to load sensor data. Cannot start server.")
