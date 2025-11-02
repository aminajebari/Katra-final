<script>
        const state = {
            pumpRunning: false,
            autoMode: false,
            humidity: 50,
            totalWater: 0,
            history: [],
            edgeAnalysisActive: false,
            selectedField: null,
        }

        document.addEventListener("DOMContentLoaded", () => {
            initFieldSelector()
            updateHumidity(50)
            logHistory("تم تهيئة النظام")
            updatePumpUI()
            document.getElementById("moistureFill").style.width = "50%"
            document.getElementById("moistureStatus").textContent = "جيد"
            document.getElementById("temperatureStatus").textContent = "متوقفة"
            document.getElementById("recommendationStatus").textContent = "جاهز"
        })

        function initFieldSelector() {
            const fields = [
                { id: '1', name: '🍅', crop: 'الطماطم' },
                { id: '2', name: '🧅', crop: 'البصل' },
                { id: '3', name: '🌿', crop: 'النعناع' }
            ]

            const selector = document.getElementById('fieldSelector')
            fields.forEach((field, index) => {
                const btn = document.createElement('button')
                btn.className = 'field-btn' + (index === 0 ? ' active' : '')
                btn.textContent = field.name
                btn.onclick = () => selectField(btn, field.crop)
                selector.appendChild(btn)
            })
            state.selectedField = 'الطماطم'
        }

        function selectField(btn, fieldName) {
            const buttons = document.querySelectorAll('.field-btn')
            buttons.forEach(b => b.classList.remove('active'))
            btn.classList.add('active')
            state.selectedField = fieldName
            logHistory(`تم اختيار الحقل: ${fieldName}`)
        }

        function updateHumidity(value) {
            state.humidity = Number.parseInt(value)
            document.getElementById("moistureValue").textContent = state.humidity + "%"
            document.getElementById("humidityDisplay").textContent = state.humidity + "%"
            document.getElementById("moistureFill").style.width = state.humidity + "%"
            
            const moistureStatus = document.getElementById("moistureStatus")
            if (state.humidity < 30) {
                moistureStatus.textContent = "حرج"
            } else if (state.humidity < 40) {
                moistureStatus.textContent = "منخفض"
            } else if (state.humidity >= 50 && state.humidity <= 70) {
                moistureStatus.textContent = "مثالي"
            } else if (state.humidity > 85) {
                moistureStatus.textContent = "مرتفع جداً"
            } else {
                moistureStatus.textContent = "جيد"
            }

            if (state.autoMode) {
                runEdgeAnalysis()
            }
        }

        function startPump() {
            if (!state.pumpRunning) {
                state.pumpRunning = true
                updatePumpUI()
                logHistory("تم تشغيل المضخة (" + (state.autoMode ? "الوضع الآلي" : "الوضع اليدوي") + ")")
                addWaterUsage()
            }
        }

        function stopPump() {
            if (state.pumpRunning) {
                state.pumpRunning = false
                updatePumpUI()
                logHistory("تم إيقاف المضخة")
            }
        }

        function toggleAutoMode() {
            state.autoMode = !state.autoMode
            updatePumpUI()

            if (state.autoMode) {
                logHistory("تم تفعيل الوضع الآلي")
                runEdgeAnalysis()
            } else {
                if (state.pumpRunning) {
                    stopPump()
                }
                logHistory("تم تفعيل الوضع اليدوي")
            }
        }

        function updatePumpUI() {
            const startBtn = document.getElementById("startBtn")
            const stopBtn = document.getElementById("stopBtn")
            const autoBtn = document.getElementById("autoBtn")
            const decisionStatement = document.getElementById("decisionStatement")
            const decisionReason = document.getElementById("decisionReason")
            const modeLabel = document.getElementById("modeLabel")
            const tempValue = document.getElementById("temperatureValue")
            const recValue = document.getElementById("recommendationValue")
            const recStatus = document.getElementById("recommendationStatus")

            startBtn.disabled = state.pumpRunning
            stopBtn.disabled = !state.pumpRunning

            if (state.pumpRunning) {
                decisionStatement.textContent = "المضخة تعمل"
                decisionStatement.className = "decision-statement water-now"
                tempValue.textContent = "تعمل"
                recValue.textContent = "🟢"
                recStatus.textContent = "نشطة"
            } else {
                decisionStatement.textContent = "المضخة متوقفة"
                decisionStatement.className = "decision-statement can-wait"
                tempValue.textContent = "متوقفة"
                recValue.textContent = "🔴"
                recStatus.textContent = "متوقفة"
            }

            if (state.autoMode) {
                autoBtn.textContent = "⚙ الوضع الآلي"
                modeLabel.textContent = "الوضع: آلي (الحوسبة الحدية نشطة)"
            } else {
                autoBtn.textContent = "⚙ الوضع اليدوي"
                modeLabel.textContent = "الوضع: يدوي"
            }
        }

        function runEdgeAnalysis() {
            state.edgeAnalysisActive = true
            const humidity = state.humidity
            let decision = ""
            let shouldWater = false

            if (humidity < 30) {
                decision = "حرج - الري فوراً"
                shouldWater = true
            } else if (humidity < 40) {
                decision = "عالي - الري قريباً"
                shouldWater = true
            } else if (humidity >= 50 && humidity <= 70) {
                decision = "مثالي - لا حاجة للري"
                shouldWater = false
            } else if (humidity > 85) {
                decision = "حرج - إيقاف الري"
                shouldWater = false
            } else {
                decision = "جيد - يمكن الري"
                shouldWater = false
            }

            const decisionReason = document.getElementById("decisionReason")
            decisionReason.textContent = decision

            if (state.autoMode) {
                if (shouldWater && !state.pumpRunning) {
                    startPump()
                } else if (!shouldWater && state.pumpRunning && humidity > 50) {
                    stopPump()
                }
            }

            logHistory("تحليل الحوسبة الحدية: " + decision)
            state.edgeAnalysisActive = false
        }

        function addWaterUsage() {
            if (state.pumpRunning) {
                state.totalWater += 0.5
                document.getElementById("humidityValue").textContent = state.totalWater.toFixed(1)
            }
        }

        function logHistory(message) {
            const now = new Date()
            const timeStr = now.toLocaleTimeString('ar-SA')

            state.history.unshift({
                time: timeStr,
                message: message,
            })

            if (state.history.length > 20) {
                state.history.pop()
            }

            updateHistoryUI()
        }

        function updateHistoryUI() {
            const historyList = document.getElementById("timelineContainer")
            if (state.history.length === 0) {
                historyList.innerHTML = '<div class="timeline-item"><div class="timeline-value">لم يتم تسجيل أي عمليات حتى الآن</div></div>'
                return
            }
            
            historyList.innerHTML = state.history
                .map((entry) => `
                    <div class="timeline-item">
                        <div class="timeline-time">${entry.time}</div>
                        <div class="timeline-data">
                            <div class="timeline-value">${entry.message}</div>
                        </div>
                    </div>
                `)
                .join("")
        }

        setInterval(() => {
            if (state.pumpRunning) {
                addWaterUsage()
            }
        }, 1000)
    </script>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">رطوبة التربة</div>
            <div class="metric-value"><span id="moistureValue">50</span>%</div>
            <div class="metric-status" id="moistureStatus">جيد</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">حالة المضخة</div>
            <div class="metric-value" id="temperatureValue">متوقفة</div>
            <div class="metric-status" id="temperatureStatus">متوقفة</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">إجمالي الماء</div>
            <div class="metric-value"><span id="humidityValue">0.0</span> لتر</div>
            <div class="metric-status" id="recommendationStatus">جاهز</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">الوضع</div>
            <div class="metric-value" id="recommendationValue">🔴</div>
            <div class="metric-status" id="decisionStatement">متوقفة</div>
        </div>
    </div>
