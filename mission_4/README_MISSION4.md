# Mission 4: Mabrouka la Prédictrice 🧠

An AI-powered watering prediction system using Machine Learning (scikit-learn) and cloud storage (Supabase).

## Features

- **AI Prediction**: Uses Linear Regression to predict watering needs
- **Daily Forecast**: Smart recommendation for today's watering
- **Weekly Planning**: 7-day intelligent watering schedule
- **Water Optimization**: Calculates water savings with AI optimization
- **Real-time Analysis**: Considers soil moisture, temperature, humidity, and rainfall

## Setup

### 1. Backend Setup

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run backend server
python mission4_backend.py
\`\`\`

Backend will run on `http://localhost:5000`

### 2. Frontend Setup

Replace in `mission4.html`:
\`\`\`javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
\`\`\`

With your actual Supabase credentials from [supabase.com](https://supabase.com)

### 3. Optional: Connect Supabase

Create a table in Supabase:
\`\`\`sql
CREATE TABLE predictions (
  id BIGSERIAL PRIMARY KEY,
  prediction_type VARCHAR(50),
  data JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

Then update `mission4_backend.py` to save predictions to Supabase.

## Usage

1. Open `mission4.html` in your browser
2. Backend fetches AI predictions
3. Dashboard displays recommendations
4. Water savings calculated automatically

## ML Model

- **Algorithm**: Linear Regression (scikit-learn)
- **Features**: Moisture, Temperature, Humidity, Rainfall, Hours Since Watering
- **Output**: Water/Don't Water decision with confidence score

## Technology Stack

- **Frontend**: HTML/CSS/JavaScript
- **Backend**: Python Flask
- **ML**: scikit-learn
- **Cloud**: Supabase (optional)
- **API**: REST

---

Made with 🌱 for Mabrouka
