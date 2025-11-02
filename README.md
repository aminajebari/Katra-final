# Smart Pump Control System

A **free, GitHub-ready** IoT solution for automated watering systems with **cloud storage**.

## Features

- ✅ **HTML/CSS/JavaScript** frontend with beautiful dashboard
- ✅ **Supabase** free cloud database (no Google, no complications)
- ✅ **Real-time monitoring** of soil humidity and pump status
- ✅ **Auto/Manual modes** for pump control
- ✅ **Complete operation history** stored in cloud
- ✅ **Fully mobile responsive**
- ✅ **Push to GitHub immediately** - no backend required

## Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** Supabase (PostgreSQL cloud - FREE)
- **Cloud Storage:** 100% free tier
- **Hosting:** GitHub Pages or any static host

## Quick Start (3 Steps)

### Step 1: Create Supabase Account (FREE)

1. Go to https://supabase.com and sign up
2. Create a new project
3. Follow the setup in `SETUP_SUPABASE.md`

### Step 2: Update Configuration

Edit `script.js` line 8-9 with your Supabase credentials:

\`\`\`javascript
const SUPABASE_URL = "YOUR_SUPABASE_URL"
const SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY"
\`\`\`

### Step 3: Push to GitHub

\`\`\`bash
git add .
git commit -m "Smart pump control system"
git push origin main
\`\`\`

Done! Open `index.html` and your data will save to cloud automatically.

## Project Structure

\`\`\`
smart-pump-control/
├── index.html              # Main frontend
├── script.js               # Frontend logic & Supabase integration
├── styles.css              # Professional styling
├── SETUP_SUPABASE.md       # Cloud setup guide
└── README.md              # This file
\`\`\`

## Usage

1. **Update Supabase credentials** in script.js
2. **Open index.html** in browser (no backend needed)
3. **Control pump:** Start/Stop buttons
4. **Switch modes:** Manual or Auto
5. **Data syncs:** Everything saves to Supabase cloud automatically

## How It Works

- **Frontend:** Pure JavaScript, no build process
- **Storage:** Supabase REST API saves data instantly
- **No backend:** All logic runs in browser
- **Completely free:** Supabase free tier covers everything

## Deployment Options

### Option 1: GitHub Pages (Recommended for free hosting)

\`\`\`bash
# Enable GitHub Pages in repository settings
# Point to main branch / root directory
# Site will be live at: https://YOUR_USERNAME.github.io/smart-pump-control
\`\`\`

### Option 2: Vercel (Also free)

\`\`\`bash
vercel deploy
\`\`\`

### Option 3: Netlify (Also free)

\`\`\`bash
netlify deploy --prod --dir .
\`\`\`

## Free Tier Limits

- **Supabase:** 500 MB storage, unlimited API calls ✅
- **Perfect for:** Home gardens, plants, hobby farms

## Troubleshooting

**Data not saving?**
- Check Supabase credentials in script.js
- Verify database table `watering_logs` exists in Supabase
- Open browser console (F12) to see error messages

**Can't see Supabase dashboard?**
- Make sure you're logged into https://supabase.com
- Check you selected the correct project

## License

MIT - Feel free to use and modify!

## Questions?

Open an issue on GitHub or check `SETUP_SUPABASE.md` for detailed setup steps.
\`\`\`

```text file=".env.local"
# Supabase Configuration
# Get these from: https://supabase.com → Project Settings → API

SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
