from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import numpy as np
from sklearn.linear_model import LinearRegression

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================
# MACHINE LEARNING MODEL
# ============================================

class WateringPredictor:
    def __init__(self):
        # Simple Linear Regression model for watering prediction
        self.model = LinearRegression()
        self.is_trained = False
        
        # Training data: [moisture, temperature, humidity, rainfall_prob, hours_since_watering]
        self.X_train = np.array([
            [30, 32, 40, 15, 36],  # Should water
            [20, 35, 30, 10, 48],  # Should water
            [15, 38, 25, 5, 60],   # Should water
            [65, 24, 60, 75, 12],  # Don't water
            [70, 20, 70, 80, 8],   # Don't water
            [55, 22, 65, 70, 10],  # Don't water
        ])
        
        # Target: 1 = water, 0 = don't water
        self.y_train = np.array([1, 1, 1, 0, 0, 0])
        
        # Train the model
        self.train()

    def train(self):
        self.model.fit(self.X_train, self.y_train)
        self.is_trained = True
        print("[v0] ML Model trained successfully")

    def predict(self, features):
        if not self.is_trained:
            return None

        # Extract features
        moisture = features['moisture']
        temperature = features['temperature']
        humidity = features['humidity']
        rainfall_probability = features['rainfall_probability']
        hours_since_watering = features['hours_since_watering']

        # Prepare input
        X = np.array([[moisture, temperature, humidity, rainfall_probability, hours_since_watering]])
        
        # Get prediction (0-1 probability)
        prediction_prob = self.model.predict(X)[0]
        
        # Decision threshold
        should_water = prediction_prob > 0.5
        confidence = abs(prediction_prob * 100) if should_water else ((1 - prediction_prob) * 100)
        confidence = min(confidence, 95)

        return {
            'should_water': bool(should_water),
            'confidence': round(confidence, 0),
            'score': float(prediction_prob),
            'factors': {
                'moisture': moisture / 100,
                'temperature': min(temperature / 40, 1),
                'humidity': humidity / 100,
                'rainfall': rainfall_probability / 100,
                'last_watering': min(hours_since_watering / 48, 1)
            }
        }

    def optimize_schedule(self, predictions, current_usage):
        optimized_usage = 0
        watering_days = []

        for pred in predictions:
            if pred['should_water']:
                # Estimate watering duration based on soil moisture
                duration = 20  # Base 20 minutes
                if pred['soil_moisture'] < 30:
                    duration += 10
                if pred['soil_moisture'] < 20:
                    duration += 10
                if pred['temperature'] > 30:
                    duration += 5

                optimized_usage += duration * 5  # 5L per minute
                watering_days.append(pred['day'])

        savings = ((current_usage - optimized_usage) / current_usage * 100)
        
        return {
            'current_usage': current_usage,
            'optimized_usage': round(optimized_usage),
            'savings_percentage': round(savings, 1),
            'savings_liters': round(current_usage - optimized_usage, 1),
            'watering_days': len(watering_days)
        }

predictor = WateringPredictor()

# ============================================
# MOCK DATA & WEATHER
# ============================================

def get_weather_forecast(days=7):
    forecast = []
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    weather_conditions = ['sunny', 'cloudy', 'rainy', 'partly_cloudy']

    for i in range(days):
        forecast.append({
            'day': day_names[i],
            'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
            'temperature': round(20 + np.random.uniform(0, 15), 1),
            'humidity': round(40 + np.random.uniform(0, 40), 1),
            'rainfall_probability': round(np.random.uniform(0, 100), 1),
            'weather_condition': weather_conditions[np.random.randint(0, len(weather_conditions))]
        })

    return forecast

def generate_reasoning(prediction, soil_data, weather):
    reasons = []
    
    if prediction['should_water']:
        if soil_data['moisture'] < 30:
            reasons.append(f"Sol très sec ({soil_data['moisture']}%)")
        if weather['temperature'] > 30:
            reasons.append(f"Température élevée ({weather['temperature']}°C)")
        if weather['rainfall_probability'] < 30:
            reasons.append(f"Peu de chances de pluie ({weather['rainfall_probability']}%)")
    else:
        if weather['rainfall_probability'] > 60:
            reasons.append(f"Forte probabilité de pluie ({weather['rainfall_probability']}%)")
        if soil_data['moisture'] > 60:
            reasons.append(f"Sol déjà bien hydraté ({soil_data['moisture']}%)")

    return '. '.join(reasons) if reasons else "Conditions normales"

# ============================================
# API ROUTES
# ============================================

@app.route('/api/prediction/daily', methods=['GET'])
def daily_prediction():
    try:
        # Get weather
        weather = get_weather_forecast(1)[0]
        
        # Mock soil data
        soil_data = {
            'moisture': round(20 + np.random.uniform(0, 60), 1),
            'temperature': weather['temperature']
        }

        # Make prediction
        prediction = predictor.predict({
            'moisture': soil_data['moisture'],
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'rainfall_probability': weather['rainfall_probability'],
            'hours_since_watering': round(np.random.uniform(12, 60), 1)
        })

        best_time = '19:00' if weather['temperature'] > 30 else '18:00'

        response = {
            'shouldWater': prediction['should_water'],
            'confidence': int(prediction['confidence']),
            'bestTime': best_time,
            'reasoning': generate_reasoning(prediction, soil_data, weather),
            'soilMoisture': int(soil_data['moisture']),
            'temperature': int(weather['temperature']),
            'rainfall': int(weather['rainfall_probability']),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"[v0] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/weekly', methods=['GET'])
def weekly_prediction():
    try:
        forecast = get_weather_forecast(7)
        
        weekly_plan = []
        for day_data in forecast:
            prediction = predictor.predict({
                'moisture': round(35 + np.random.uniform(-20, 20), 1),
                'temperature': day_data['temperature'],
                'humidity': day_data['humidity'],
                'rainfall_probability': day_data['rainfall_probability'],
                'hours_since_watering': round(np.random.uniform(24, 72), 1)
            })

            best_time = '19:00' if day_data['temperature'] > 30 else '18:00'

            weekly_plan.append({
                'day': day_data['day'],
                'shouldWater': prediction['should_water'],
                'confidence': int(prediction['confidence']),
                'bestTime': best_time,
                'weather': day_data['weather_condition'],
                'temperature': int(day_data['temperature']),
                'rainfall': int(day_data['rainfall_probability'])
            })

        return jsonify(weekly_plan), 200

    except Exception as e:
        print(f"[v0] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/optimize', methods=['GET'])
def optimize_prediction():
    try:
        forecast = get_weather_forecast(7)
        current_usage = 200

        predictions = []
        for day_data in forecast:
            pred = predictor.predict({
                'moisture': round(35 + np.random.uniform(-20, 20), 1),
                'temperature': day_data['temperature'],
                'humidity': day_data['humidity'],
                'rainfall_probability': day_data['rainfall_probability'],
                'hours_since_watering': round(np.random.uniform(24, 72), 1)
            })

            predictions.append({
                'day': day_data['day'],
                'should_water': pred['should_water'],
                'temperature': day_data['temperature'],
                'soil_moisture': round(35 + np.random.uniform(-20, 20), 1)
            })

        optimization = predictor.optimize_schedule(predictions, current_usage)

        return jsonify(optimization), 200

    except Exception as e:
        print(f"[v0] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'Mission 4 - AI Prediction',
        'model_version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("🧠 Mission 4 - AI Prediction Backend")
    print(f"🚀 Starting server on http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET http://localhost:5000/api/prediction/daily")
    print("  GET http://localhost:5000/api/prediction/weekly")
    print("  GET http://localhost:5000/api/prediction/optimize")
    print("  GET http://localhost:5000/health")
    
    app.run(debug=True, port=5000)
