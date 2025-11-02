// Supabase Configuration
const SUPABASE_URL = "YOUR_SUPABASE_URL" // Replace with your Supabase URL
const SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY" // Replace with your Supabase key
const { createClient } = window.supabase
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// State variables
let pumpRunning = false
let autoMode = false
let currentHumidity = 50
let totalWater = 0

class RemoteMonitoringDashboard {
  constructor() {
    this.alerts = []
    this.pumpOn = false
    this.init()
  }

  init() {
    this.checkCloudConnection()
    this.updateDashboard()
    setInterval(() => this.updateDashboard(), 4000)
  }

  async checkCloudConnection() {
    try {
      const { data, error } = await supabase.from("sensor_readings").select("count", { count: "exact" })
      if (error) throw error
      this.setCloudStatus(true)
    } catch (error) {
      console.log("[v0] Cloud connection failed:", error.message)
      this.setCloudStatus(false)
    }
  }

  setCloudStatus(isOnline) {
    const statusDot = document.getElementById("cloudStatusDot")
    const statusText = document.getElementById("cloudStatusText")
    if (isOnline) {
      statusDot.className = "status-dot online"
      statusText.textContent = "Connexion Cloud: Connecté ✓"
    } else {
      statusDot.className = "status-dot offline"
      statusText.textContent = "Connexion Cloud: Hors ligne ✗"
    }
  }

  async saveReadingToCloud(humidity) {
    try {
      const { data, error } = await supabase.from("sensor_readings").insert([
        {
          humidity: humidity,
          timestamp: new Date().toISOString(),
          created_at: new Date().toISOString(),
        },
      ])
      if (error) throw error
      console.log("[v0] Reading saved to cloud")
      await this.loadCloudStats()
    } catch (error) {
      console.log("[v0] Error saving reading:", error.message)
    }
  }

  async loadCloudStats() {
    try {
      const { data: readings, error: readError } = await supabase
        .from("sensor_readings")
        .select("*", { count: "exact" })

      const { data: operations, error: opError } = await supabase
        .from("pump_operations")
        .select("*", { count: "exact" })

      if (!readError && readings) {
        document.getElementById("syncedReadings").textContent = readings.length
      }
      if (!opError && operations) {
        document.getElementById("syncedOperations").textContent = operations.length
      }
    } catch (error) {
      console.log("[v0] Error loading cloud stats:", error.message)
    }
  }

  updateDashboard() {
    const moisture = 30 + Math.random() * 50
    const temp = 20 + Math.random() * 15
    const waterLevel = 40 + Math.random() * 60
    this.pumpOn = Math.random() > 0.6

    // Update metrics
    document.getElementById("moisture").textContent = moisture.toFixed(1) + "%"
    document.getElementById("moisture-status").textContent =
      moisture < 35 ? "⚠️ Faible" : moisture < 60 ? "✓ Normal" : "✓ Optimal"

    document.getElementById("temperature").textContent = temp.toFixed(1) + "°C"
    document.getElementById("temp-status").textContent = temp > 32 ? "⚠️ Élevée" : temp > 25 ? "✓ Normale" : "✓ Fraîche"

    document.getElementById("water-level").textContent = waterLevel.toFixed(1) + "%"
    document.getElementById("water-progress").style.width = waterLevel.toFixed(1) + "%"

    const pumpCard = document.getElementById("pump-card")
    if (this.pumpOn) {
      pumpCard.classList.add("active")
      document.getElementById("pump-status").textContent = "✅ Active"
      document.getElementById("pump-text").textContent = "Arrosage en cours"
    } else {
      pumpCard.classList.remove("active")
      document.getElementById("pump-status").textContent = "⏸ Arrêtée"
      document.getElementById("pump-text").textContent = "En attente"
    }

    document.getElementById("last-update").textContent = new Date().toLocaleTimeString("fr-FR")

    this.saveReadingToCloud(moisture)

    // Generate alerts
    if (moisture < 35 && Math.random() > 0.7) {
      this.addAlert("warning", "💧 Sol trop sec", "Arrosage recommandé")
    }
    if (waterLevel < 50 && Math.random() > 0.8) {
      this.addAlert("info", "📊 Niveau d'eau faible", "Prévoir ravitaillement")
    }
    if (temp > 32 && Math.random() > 0.85) {
      this.addAlert("warning", "🌡️ Température élevée", "Surveillance accrue nécessaire")
    }
  }

  addAlert(type, title, message) {
    const alert = {
      id: Date.now(),
      type,
      title,
      message,
      time: new Date().toLocaleTimeString("fr-FR"),
      resolved: false,
    }

    this.alerts.unshift(alert)
    if (this.alerts.length > 5) this.alerts.pop()
    this.renderAlerts()
  }

  resolveAlert(id) {
    const alert = this.alerts.find((a) => a.id === id)
    if (alert) {
      alert.resolved = true
      this.renderAlerts()
    }
  }

  renderAlerts() {
    const container = document.getElementById("alerts-container")
    const activeCount = this.alerts.filter((a) => !a.resolved).length
    document.getElementById("alert-count").textContent = activeCount + " " + (activeCount === 1 ? "active" : "actives")

    if (this.alerts.length === 0) {
      container.innerHTML = `
                <div class="alerts-empty">
                    <div class="empty-icon">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"></path>
                        </svg>
                    </div>
                    <h4>Tout va bien!</h4>
                    <p>Aucune alerte pour le moment. Ta ferme est en bonne santé 🌱</p>
                </div>
            `
      return
    }

    container.innerHTML = `<div class="alerts-list">
            ${this.alerts
              .map(
                (alert) => `
                <div class="alert-item ${alert.type} ${alert.resolved ? "resolved" : ""}">
                    <div class="alert-content">
                        <svg class="alert-icon" fill="currentColor" viewBox="0 0 24 24">
                            ${alert.type === "warning" ? '<path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"></path>' : '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path>'}
                        </svg>
                        <div class="alert-body">
                            <div class="alert-title">
                                <h4>${alert.title}</h4>
                                ${alert.resolved ? '<span class="alert-badge">✓ Résolue</span>' : ""}
                            </div>
                            <p class="alert-message">${alert.message}</p>
                            <div class="alert-time">⏰ ${alert.time}</div>
                        </div>
                    </div>
                    ${!alert.resolved ? `<button class="alert-button" onclick="dashboard.resolveAlert(${alert.id})">Marquer résolu</button>` : ""}
                </div>
            `,
              )
              .join("")}
        </div>`
  }
}

const dashboard = new RemoteMonitoringDashboard()

// Initialize app
document.addEventListener("DOMContentLoaded", async () => {
  await checkCloudConnection()
  await loadDataFromCloud()
  updateUI()
})

async function checkCloudConnection() {
  try {
    const { data, error } = await supabase.from("pump_operations").select("count", { count: "exact" })
    if (error) throw error
    setCloudStatus(true)
  } catch (error) {
    console.log("Cloud connection failed:", error.message)
    setCloudStatus(false)
  }
}

function setCloudStatus(isOnline) {
  const statusDot = document.getElementById("cloudStatus")
  const statusText = document.getElementById("cloudStatusText")
  if (isOnline) {
    statusDot.className = "status-dot online"
    statusText.textContent = "En ligne"
  } else {
    statusDot.className = "status-dot offline"
    statusText.textContent = "Hors ligne"
  }
}

function updateHumidity(value) {
  currentHumidity = Number.parseInt(value)
  document.getElementById("humidityDisplay").textContent = currentHumidity + "%"
  document.getElementById("humidityValue").textContent = currentHumidity + "%"
  document.getElementById("humidityFill").style.width = currentHumidity + "%"

  // Auto-trigger watering in auto mode
  if (autoMode) {
    analyzeAndDecide()
  }
}

async function startPump() {
  pumpRunning = true
  document.getElementById("startBtn").disabled = true
  document.getElementById("stopBtn").disabled = false
  document.getElementById("pumpStatus").textContent = "En cours..."
  document.getElementById("statusIndicator").textContent = "EN COURS"
  document.getElementById("statusIndicator").className = "status-indicator running"

  await saveOperation("POMPE_DÉMARRÉE", currentHumidity, 0)
}

async function stopPump() {
  pumpRunning = false
  document.getElementById("startBtn").disabled = false
  document.getElementById("stopBtn").disabled = true
  document.getElementById("pumpStatus").textContent = "Arrêtée"
  document.getElementById("statusIndicator").textContent = "ARRÊTÉE"
  document.getElementById("statusIndicator").className = "status-indicator stopped"

  await saveOperation("POMPE_ARRÊTÉE", currentHumidity, 2)
}

async function toggleAutoMode() {
  autoMode = !autoMode
  const btn = document.getElementById("autoBtn")
  const label = document.getElementById("modeLabel")

  if (autoMode) {
    btn.textContent = "⚙ Mode Auto"
    label.textContent = "Mode: Auto"
    await saveOperation("MODE_AUTO_ACTIVÉ", currentHumidity, 0)
  } else {
    btn.textContent = "⚙ Mode Manuel"
    label.textContent = "Mode: Manuel"
    await saveOperation("MODE_MANUEL_ACTIVÉ", currentHumidity, 0)
  }
}

async function analyzeAndDecide() {
  let decision = "Pas d'action"
  let waterAmount = 0

  if (currentHumidity < 30) {
    decision = "URGENT: Arroser maintenant!"
    waterAmount = 5
    if (!pumpRunning) await startPump()
  } else if (currentHumidity < 40) {
    decision = "Humidité faible - Arroser"
    waterAmount = 3
    if (!pumpRunning) await startPump()
  } else if (currentHumidity > 85) {
    decision = "Humidité trop élevée - Arrêter"
    if (pumpRunning) await stopPump()
  } else {
    decision = "Humidité optimale"
    if (pumpRunning) await stopPump()
  }

  totalWater += waterAmount
  document.getElementById("totalWater").textContent = totalWater

  await saveOperation(`ANALYSE: ${decision}`, currentHumidity, waterAmount)
}

async function saveReading() {
  const timestamp = new Date().toISOString()

  const { data, error } = await supabase.from("sensor_readings").insert([
    {
      humidity: currentHumidity,
      timestamp: timestamp,
      created_at: new Date().toISOString(),
    },
  ])

  if (error) {
    alert("Erreur sauvegarde: " + error.message)
    return
  }

  await loadDataFromCloud()
  addHistoryItem(new Date().toLocaleTimeString(), `Lecture sauvegardée: ${currentHumidity}%`)
}

async function saveOperation(action, humidity, waterUsed) {
  const { data, error } = await supabase.from("pump_operations").insert([
    {
      action: action,
      humidity: humidity,
      water_used: waterUsed,
      timestamp: new Date().toISOString(),
      created_at: new Date().toISOString(),
    },
  ])

  if (error) {
    console.log("Erreur sauvegarde opération:", error.message)
    return
  }

  addHistoryItem(new Date().toLocaleTimeString(), action)
}

async function loadDataFromCloud() {
  try {
    // Load operations
    const { data: operations, error: opError } = await supabase
      .from("pump_operations")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50)

    if (opError) throw opError

    // Load readings
    const { data: readings, error: readError } = await supabase
      .from("sensor_readings")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100)

    if (readError) throw readError

    // Update UI with cloud data
    document.getElementById("totalOperations").textContent = operations?.length || 0
    document.getElementById("totalReadings").textContent = readings?.length || 0

    // Populate history
    const historyList = document.getElementById("historyList")
    historyList.innerHTML = ""

    if (operations && operations.length > 0) {
      operations.forEach((op) => {
        const time = new Date(op.timestamp).toLocaleTimeString()
        addHistoryItem(time, `${op.action} (Humidité: ${op.humidity}%)`)
      })
    } else {
      historyList.innerHTML =
        '<div class="history-item"><span class="time">--:--:--</span><span class="action">En attente d\'opérations...</span></div>'
    }

    setCloudStatus(true)
  } catch (error) {
    console.log("Erreur chargement cloud:", error.message)
    setCloudStatus(false)
  }
}

async function refreshHistory() {
  await loadDataFromCloud()
}

async function clearHistory() {
  if (confirm("Êtes-vous sûr de vouloir effacer tout l'historique?")) {
    const { error: opError } = await supabase.from("pump_operations").delete().neq("id", 0)
    const { error: readError } = await supabase.from("sensor_readings").delete().neq("id", 0)

    if (!opError && !readError) {
      await loadDataFromCloud()
      alert("Historique effacé avec succès")
    }
  }
}

// Add item to history UI
function addHistoryItem(time, action) {
  const historyList = document.getElementById("historyList")
  if (historyList.querySelector(".history-item .action").textContent === "En attente d'opérations...") {
    historyList.innerHTML = ""
  }

  const item = document.createElement("div")
  item.className = "history-item"
  item.innerHTML = `<span class="time">${time}</span><span class="action">${action}</span>`
  historyList.insertBefore(item, historyList.firstChild)
}

// Update UI
function updateUI() {
  document.getElementById("humidityValue").textContent = currentHumidity + "%"
  document.getElementById("humidityDisplay").textContent = currentHumidity + "%"
  document.getElementById("humidityFill").style.width = currentHumidity + "%"
  document.getElementById("totalWater").textContent = totalWater
}
