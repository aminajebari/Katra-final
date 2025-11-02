// Smart Pump State Management
const state = {
  pumpRunning: false,
  autoMode: false,
  humidity: 50,
  totalWater: 0,
  history: [],
  edgeAnalysisActive: false,
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  updateHumidity(50)
  logHistory("Système initié")
})

// Update Humidity Display
function updateHumidity(value) {
  state.humidity = Number.parseInt(value)
  document.getElementById("humidityValue").textContent = state.humidity + "%"
  document.getElementById("humidityDisplay").textContent = state.humidity + "%"
  document.getElementById("humidityFill").style.width = state.humidity + "%"

  // Auto-trigger analysis if in auto mode
  if (state.autoMode) {
    runEdgeAnalysis()
  }
}

// Start Pump
function startPump() {
  if (!state.pumpRunning) {
    state.pumpRunning = true
    updatePumpUI()
    logHistory("Pompe démarrée (Mode " + (state.autoMode ? "Auto" : "Manuel") + ")")
    addWaterUsage()
  }
}

// Stop Pump
function stopPump() {
  if (state.pumpRunning) {
    state.pumpRunning = false
    updatePumpUI()
    logHistory("Pompe arrêtée")
  }
}

// Toggle Auto Mode
function toggleAutoMode() {
  state.autoMode = !state.autoMode
  updatePumpUI()

  if (state.autoMode) {
    logHistory("Mode AUTO activé - Analyse Edge Computing active")
    runEdgeAnalysis()
  } else {
    if (state.pumpRunning) {
      stopPump()
    }
    logHistory("Mode Manuel activé")
  }
}

// Update UI
function updatePumpUI() {
  const startBtn = document.getElementById("startBtn")
  const stopBtn = document.getElementById("stopBtn")
  const autoBtn = document.getElementById("autoBtn")
  const statusIndicator = document.getElementById("statusIndicator")
  const pumpStatus = document.getElementById("pumpStatus")
  const modeLabel = document.getElementById("modeLabel")

  // Pump buttons
  startBtn.disabled = state.pumpRunning
  stopBtn.disabled = !state.pumpRunning

  // Status
  if (state.pumpRunning) {
    statusIndicator.textContent = "EN MARCHE"
    statusIndicator.style.backgroundColor = "#10b981"
    pumpStatus.textContent = "En marche"
  } else {
    statusIndicator.textContent = "ARRÊTÉE"
    statusIndicator.style.backgroundColor = "#ef4444"
    pumpStatus.textContent = "Arrêtée"
  }

  // Mode
  if (state.autoMode) {
    autoBtn.textContent = "⚙ Mode Auto"
    modeLabel.textContent = "Mode: AUTO (Edge Computing Actif)"
    modeLabel.style.borderLeftColor = "#0ea5e9"
    modeLabel.style.color = "#0ea5e9"
  } else {
    autoBtn.textContent = "⚙ Mode Manuel"
    modeLabel.textContent = "Mode: Manuel"
    modeLabel.style.borderLeftColor = "#10b981"
    modeLabel.style.color = "#10b981"
  }
}

// Edge Computing Analysis (Python Logic Simulation)
function runEdgeAnalysis() {
  state.edgeAnalysisActive = true
  const humidity = state.humidity
  let decision = ""
  let shouldWater = false

  if (humidity < 30) {
    decision = "CRITIQUE - Arroser immédiatement (humidité < 30%)"
    shouldWater = true
  } else if (humidity < 40) {
    decision = "ÉLEVÉ - Arroser bientôt (humidité < 40%)"
    shouldWater = true
  } else if (humidity >= 50 && humidity <= 70) {
    decision = "OPTIMAL - Pas d'arrosage nécessaire"
    shouldWater = false
  } else if (humidity > 85) {
    decision = "CRITIQUE - Arrêter arrosage (risque de pourriture)"
    shouldWater = false
  } else {
    decision = "BON - Peut arroser si nécessaire"
    shouldWater = false
  }

  const analysisResult = document.getElementById("analysisResult")
  const analysisDescription = document.getElementById("analysisDescription")

  analysisResult.textContent = decision.split(" - ")[0]
  analysisDescription.textContent = "Décision: " + decision

  saveToGoogleSheets({
    humidity: humidity,
    pumpRunning: state.pumpRunning,
    totalWater: state.totalWater,
    decision: decision,
    mode: state.autoMode ? "AUTO" : "MANUEL",
  })

  if (state.autoMode) {
    if (shouldWater && !state.pumpRunning) {
      startPump()
    } else if (!shouldWater && state.pumpRunning && humidity > 50) {
      stopPump()
    }
  }

  logHistory("Edge Analysis: " + decision)
  state.edgeAnalysisActive = false
}

// Water Usage
function addWaterUsage() {
  if (state.pumpRunning) {
    state.totalWater += 0.5 // Simulate 0.5L per interval
    document.getElementById("totalWater").textContent = state.totalWater.toFixed(1)
  }
}

// History Logging
function logHistory(message) {
  const now = new Date()
  const timeStr = now.toLocaleTimeString()

  state.history.unshift({
    time: timeStr,
    message: message,
  })

  // Keep last 20 entries
  if (state.history.length > 20) {
    state.history.pop()
  }

  updateHistoryUI()
}

function updateHistoryUI() {
  const historyList = document.getElementById("historyList")
  historyList.innerHTML = state.history
    .map(
      (entry) => `
        <div class="history-item">
            <span class="time">${entry.time}</span>
            <span class="action">${entry.message}</span>
        </div>
    `,
    )
    .join("")
}

// Simulate pump water usage over time
setInterval(() => {
  if (state.pumpRunning) {
    addWaterUsage()
  }
}, 1000)

// Google Sheets integration configuration
const GOOGLE_SHEETS_CONFIG = {
  apiKey: "YOUR_GOOGLE_API_KEY", // Add your API key in environment
  sheetId: "YOUR_SHEET_ID", // Add your Sheet ID
  range: "Watering!A:F",
}

// Function to send data to Google Sheets
async function saveToGoogleSheets(data) {
  try {
    const response = await fetch("/api/save-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        humidity: data.humidity,
        pumpRunning: data.pumpRunning,
        totalWater: data.totalWater,
        decision: data.decision,
        mode: data.mode,
      }),
    })

    if (!response.ok) {
      console.error("[v0] Failed to save to Google Sheets:", response.statusText)
    }
  } catch (error) {
    console.error("[v0] Error saving to Google Sheets:", error)
  }
}
