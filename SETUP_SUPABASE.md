# Setup Cloud Storage with Supabase

## Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with email or GitHub
4. Create a new project

## Step 2: Create Database Tables
In your Supabase dashboard, go to SQL Editor and run:

\`\`\`sql
-- Create sensor readings table
CREATE TABLE sensor_readings (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  humidity INT NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pump operations table
CREATE TABLE pump_operations (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  action TEXT NOT NULL,
  humidity INT,
  water_used INT DEFAULT 0,
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

## Step 3: Enable Realtime (Optional)
Go to Database > Replication and enable realtime for both tables.

## Step 4: Get Your Credentials
1. Go to Settings > API
2. Copy your `Project URL` (SUPABASE_URL)
3. Copy your `anon public` key (SUPABASE_KEY)

## Step 5: Update index.html
Replace in script.js:
\`\`\`javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
\`\`\`

With your actual credentials from Step 4.

## Step 6: Test
1. Open index.html in browser
2. Check if cloud status shows "En ligne"
3. Test pump controls and sensor readings
4. All data will be saved to Supabase cloud

## Security Note
For production, use Row Level Security (RLS) policies in Supabase to protect your data.
