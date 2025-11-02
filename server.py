"""
Smart Pump Backend Server
Handles Google Sheets integration and edge computing analysis
"""

from flask import Flask, request, jsonify
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

app = Flask(__name__)

def init_google_sheets():
    """Initialize Google Sheets connection"""
    try:
        # Use service account credentials from environment
        creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS', '{}'))
        
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet('Watering')
        
        return worksheet
    except Exception as e:
        print(f"[v0] Error initializing Google Sheets: {e}")
        return None

# Initialize on startup
WORKSHEET = init_google_sheets()

@app.route('/api/save-data', methods=['POST'])
def save_data():
    """Save sensor data to Google Sheets"""
    try:
        data = request.json
        
        row = [
            data.get('timestamp'),
            data.get('humidity'),
            data.get('pumpRunning'),
            data.get('totalWater'),
            data.get('decision'),
            data.get('mode')
        ]
        
        # Append to Google Sheets
        if WORKSHEET:
            WORKSHEET.append_row(row)
            print(f"[v0] Data saved: {row}")
        
        return jsonify({'status': 'success', 'message': 'Data saved to Google Sheets'})
    
    except Exception as e:
        print(f"[v0] Error saving data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/edge-analysis', methods=['POST'])
def edge_analysis():
    """Run edge computing analysis on sensor data"""
    try:
        data = request.json
        humidity = data.get('humidity', 50)
        
        decision = analyze_watering(humidity)
        
        # Save analysis result
        row = [
            datetime.now().isoformat(),
            humidity,
            False,
            0,
            decision['action'],
            'EDGE_ANALYSIS'
        ]
        
        if WORKSHEET:
            WORKSHEET.append_row(row)
        
        return jsonify(decision)
    
    except Exception as e:
        print(f"[v0] Error in edge analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def analyze_watering(humidity):
    """Edge Computing: Analyze humidity and make watering decision"""
    
    if humidity < 30:
        return {
            'action': 'CRITIQUE - Arroser immédiatement',
            'should_water': True,
            'urgency': 'CRITICAL',
            'duration': 15
        }
    elif humidity < 40:
        return {
            'action': 'ÉLEVÉ - Arroser bientôt',
            'should_water': True,
            'urgency': 'HIGH',
            'duration': 12
        }
    elif humidity <= 70:
        return {
            'action': 'OPTIMAL - Pas d\'arrosage',
            'should_water': False,
            'urgency': 'NORMAL',
            'duration': 0
        }
    elif humidity <= 85:
        return {
            'action': 'BON - Peut arroser si nécessaire',
            'should_water': False,
            'urgency': 'NORMAL',
            'duration': 0
        }
    else:
        return {
            'action': 'CRITIQUE - Arrêter arrosage',
            'should_water': False,
            'urgency': 'CRITICAL',
            'duration': 0
        }

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retrieve watering history from Google Sheets"""
    try:
        if WORKSHEET:
            records = WORKSHEET.get_all_records()
            return jsonify({'status': 'success', 'data': records})
        return jsonify({'status': 'error', 'message': 'Sheet not initialized'}), 500
    
    except Exception as e:
        print(f"[v0] Error retrieving history: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("[v0] Starting Smart Pump Backend Server...")
    app.run(debug=True, port=5000)
