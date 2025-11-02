"""
Setup script for Google Sheets integration
Creates necessary sheet structure and authentication
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

def setup_google_sheets():
    """Initialize Google Sheets with proper structure"""
    
    print("[v0] Setting up Google Sheets integration...")
    
    try:
        # Load credentials
        creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS', '{}'))
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Get or create spreadsheet
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        sheet = client.open_by_key(sheet_id)
        
        # Create 'Watering' worksheet if it doesn't exist
        try:
            worksheet = sheet.worksheet('Watering')
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet('Watering', rows=1000, cols=6)
        
        # Add headers
        headers = ['Timestamp', 'Humidity (%)', 'Pump Running', 'Total Water (L)', 'Decision', 'Mode']
        worksheet.append_row(headers)
        
        print("[v0] Google Sheets setup complete!")
        print(f"[v0] Sheet ID: {sheet_id}")
        print("[v0] Columns: Timestamp, Humidity, Pump Status, Water Used, Decision, Mode")
        
    except Exception as e:
        print(f"[v0] Error setting up Google Sheets: {e}")
        print("[v0] Make sure to set GOOGLE_SHEETS_CREDENTIALS and GOOGLE_SHEET_ID environment variables")

if __name__ == '__main__':
    setup_google_sheets()
