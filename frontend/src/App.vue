<script setup>
import { ref, computed, onMounted } from 'vue'
import { ShieldExclamationIcon, ChatBubbleLeftEllipsisIcon, CheckCircleIcon, SparklesIcon, ChartBarIcon, TrashIcon, ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

// Sample messages pool for refresh
const sampleMessagesPools = {
  Instagram: [
    "Ich vermisse meine Mutter so sehr. Es tut immer noch weh.",
    "Danke für die schönen Worte zu meinem Großvater.",
    "Wie lange braucht ihr normalerweise für eine Antwort?",
    "Ihr seid einfach die Besten! Vielen Dank dafür!"
  ],
  Facebook: [
    "Was kostet das Premium-Paket?",
    "Kann man auch Ratenzahlung machen?",
    "Wann startet das neue Angebot?",
    "Sehr guter Service, empfehle ich weiter!"
  ],
  Twitter: [
    "RIP an alle Verstorbenen 🕊️",
    "Eure Seite hat mir geholfen.",
    "Preise sind zu hoch",
    "Bester Service ever!"
  ],
  LinkedIn: [
    "Excellente Dienstleistung im Bereich Trauerbewältigung.",
    "Interessantes Geschäftsmodell.",
    "Hohe Qualitätsstandards beeindruckend.",
    "Großartige Initiative!"
  ],
  DM: [
    "Hallo, ich brauche dringend Hilfe.",
    "Können Sie mich anrufen?",
    "Mein Termin funktioniert nicht.",
    "Vielen Dank für alles!"
  ]
}

// State
const activeTab = ref('inbox')
const selectedPlatform = ref('All')
const incomingMessages = ref([
  { id: 1, text: "Ich bin so unglaublich traurig und weiß nicht mehr weiter. Mein Vater ist gerade gestorben...", platform: "Instagram" },
  { id: 2, text: "Was kostet das Basis-Paket bei euch? Finde die Preisliste nicht.", platform: "Facebook" },
  { id: 3, text: "Vielen Dank für den tollen und informativen Beitrag gestern!", platform: "LinkedIn" },
  { id: 4, text: "Ich kann nicht weiterleben. Alles ist hoffnungslos.", platform: "DM" }
])

const processedMessages = ref([])
const isAnalyzing = ref(false)
const analytics = ref({})
const highPriorityMessages = ref([])
const toastMessage = ref('')
const toastType = ref('success') // 'success', 'error', 'info'
const showToast = ref(false)

const apiUrl = 'http://localhost:8000'

// Auto-increment ID
let nextId = 5

// Computed
const filteredIncoming = computed(() => {
  if (selectedPlatform.value === 'All') return incomingMessages.value
  return incomingMessages.value.filter(m => m.platform === selectedPlatform.value)
})

const unprocessedCount = computed(() => incomingMessages.value.length)
const processedCount = computed(() => processedMessages.value.length)
const highPriorityCount = computed(() => analytics.value.high_priority_count || 0)

// Toast notification
const showNotification = (msg, type = 'success', duration = 3000) => {
  toastMessage.value = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, duration)
}

// Fetch analytics
const loadAnalytics = async () => {
  try {
    const response = await fetch(`${apiUrl}/api/analytics`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    analytics.value = data
  } catch (error) {
    console.error("Failed to load analytics:", error)
    showNotification(`Analytics: ${error.message}`, 'error')
  }
}

// Fetch high priority
const loadHighPriority = async () => {
  try {
    const response = await fetch(`${apiUrl}/api/messages/high-priority`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    highPriorityMessages.value = data.messages || []
  } catch (error) {
    console.error("Failed to load high priority:", error)
  }
}

// Refresh all data
const refreshAll = async () => {
  await loadAnalytics()
  await loadHighPriority()
  showNotification('Data refreshed', 'success')
}

// Validate message input
const validateMessage = (msg) => {
  if (!msg.text || msg.text.trim().length < 5) {
    throw new Error("Message must be at least 5 characters long")
  }
  if (msg.text.length > 2000) {
    throw new Error("Message cannot exceed 2000 characters")
  }
  if (!msg.platform || msg.platform.trim().length === 0) {
    throw new Error("Platform must be selected")
  }
  const validPlatforms = ['Instagram', 'Facebook', 'Twitter', 'LinkedIn', 'DM', 'Manual']
  if (!validPlatforms.includes(msg.platform)) {
    throw new Error(`Invalid platform. Must be one of: ${validPlatforms.join(', ')}`)
  }
}

// Triage single message (stay on inbox)
const triageMessage = async (msg) => {
  isAnalyzing.value = true
  try {
    validateMessage(msg)
    
    const response = await fetch(`${apiUrl}/api/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: msg.id,
        text: msg.text,
        platform: msg.platform
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()

    // Remove from incoming
    incomingMessages.value = incomingMessages.value.filter(m => m.id !== msg.id)

    // Add to processed
    processedMessages.value.unshift({
      ...msg,
      ...data.analysis,
      suggested_reply: data.suggested_reply,
      timestamp: new Date().toISOString()
    })

    // Refresh analytics
    await loadAnalytics()
    await loadHighPriority()

    showNotification(`Message #${msg.id} analyzed successfully!`, 'success')

  } catch (error) {
    console.error("Triage failed:", error)
    showNotification(`Error: ${error.message}`, 'error', 5000)
  }
  isAnalyzing.value = false
}

// Batch triage
const batchTriage = async () => {
  if (incomingMessages.value.length === 0) {
    showNotification("No messages to analyze", 'info')
    return
  }
  
  isAnalyzing.value = true
  try {
    // Validate all
    incomingMessages.value.forEach(validateMessage)
    
    const response = await fetch(`${apiUrl}/api/triage/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: incomingMessages.value
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()

    // Move all to processed
    data.results.forEach((result, idx) => {
      processedMessages.value.unshift({
        id: result.message_id,
        text: incomingMessages.value[idx].text,
        platform: incomingMessages.value[idx].platform,
        ...result.analysis,
        suggested_reply: result.suggested_reply,
        timestamp: new Date().toISOString()
      })
    })

    incomingMessages.value = []

    // Refresh
    await loadAnalytics()
    await loadHighPriority()

    showNotification(`${data.count} messages analyzed successfully!`, 'success')

  } catch (error) {
    console.error("Batch triage failed:", error)
    showNotification(`Batch Error: ${error.message}`, 'error', 5000)
  }
  isAnalyzing.value = false
}

// Clear history
const clearHistory = async () => {
  if (!confirm("Clear all message history? This cannot be undone.")) return
  
  try {
    const response = await fetch(`${apiUrl}/api/clear-history`, { method: 'POST' })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    
    const data = await response.json()
    processedMessages.value = []
    incomingMessages.value = []
    analytics.value = {}
    highPriorityMessages.value = []
    showNotification(data.message, 'success')
  } catch (error) {
    console.error("Failed to clear history:", error)
    showNotification(`Error: ${error.message}`, 'error')
  }
}

// Add manual message
const newMessageText = ref('')
const newMessagePlatform = ref('Manual')
const messageError = ref('')

const addManualMessage = () => {
  messageError.value = ''
  
  try {
    if (!newMessageText.value || newMessageText.value.trim().length < 5) {
      throw new Error("Message must be at least 5 characters")
    }
    if (newMessageText.value.length > 2000) {
      throw new Error("Message cannot exceed 2000 characters")
    }
    
    incomingMessages.value.push({
      id: nextId++,
      text: newMessageText.value.trim(),
      platform: newMessagePlatform.value
    })
    
    newMessageText.value = ''
    showNotification("Message added to inbox", 'success')
  } catch (error) {
    messageError.value = error.message
    showNotification(`Input Error: ${error.message}`, 'error')
  }
}

// Refresh with random new messages (5-20 new, max 20 total, keep existing)
const refreshWithNewMessages = () => {
  const platforms = ['Instagram', 'Facebook', 'Twitter', 'LinkedIn', 'DM']
  const newCount = Math.floor(Math.random() * 16) + 5 // 5-20 new messages
  
  for (let i = 0; i < newCount; i++) {
    const platform = platforms[Math.floor(Math.random() * platforms.length)]
    const messages = sampleMessagesPools[platform]
    const randomMsg = messages[Math.floor(Math.random() * messages.length)]
    
    incomingMessages.value.push({
      id: nextId++,
      text: randomMsg,
      platform: platform
    })
  }
  
  // Keep max 20 total (remove oldest if exceeds)
  if (incomingMessages.value.length > 20) {
    incomingMessages.value = incomingMessages.value.slice(-20)
  }
  
  showNotification(`Added ${Math.min(newCount, 20)} new messages`, 'info')
}

// Styling
const getUrgencyColor = (urgency) => {
  if (urgency === 'High') return 'bg-red-500/20 text-red-400 border-red-500/30'
  if (urgency === 'Medium') return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
}

const getEmotionIntensity = (score) => {
  if (score >= 80) return 'Extreme'
  if (score >= 60) return 'High'
  if (score >= 40) return 'Moderate'
  return 'Low'
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-200 font-sans">

    <!-- Toast Notification -->
    <transition name="slide-up">
      <div v-if="showToast" :class="['fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg border z-50 animate-pulse', 
        toastType === 'success' ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400' :
        toastType === 'error' ? 'bg-red-500/20 border-red-500/30 text-red-400' :
        'bg-blue-500/20 border-blue-500/30 text-blue-400']">
        {{ toastMessage }}
      </div>
    </transition>

    <!-- Header -->
    <header class="sticky top-0 z-50 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 md:px-8 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <SparklesIcon class="w-8 h-8 text-indigo-400" />
          <div>
            <h1 class="text-2xl font-bold text-white">Aura</h1>
            <p class="text-xs text-slate-400">v1.0 • Semantic Triage & Analytics</p>
          </div>
        </div>
        
        <div class="flex items-center gap-4">
          <div :class="['text-xs font-medium px-3 py-2 rounded-lg border flex items-center gap-2', 
            isAnalyzing ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : 'bg-slate-800 text-slate-400 border-slate-700']">
            <div :class="['w-2 h-2 rounded-full', isAnalyzing ? 'bg-yellow-400 animate-pulse' : 'bg-emerald-400']"></div>
            {{ isAnalyzing ? 'Processing...' : 'Ready' }}
          </div>
          <button @click="loadAnalytics" :disabled="isAnalyzing" class="text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-slate-700/50 transition disabled:opacity-50">
            <ArrowPathIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="max-w-7xl mx-auto px-4 md:px-8 flex gap-1 border-t border-slate-700/50 overflow-x-auto">
        <button @click="activeTab = 'inbox'" :class="['px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap', activeTab === 'inbox' ? 'text-indigo-400 border-indigo-400' : 'text-slate-400 border-transparent hover:text-slate-300']">
          Inbox ({{ unprocessedCount }})
        </button>
        <button @click="activeTab = 'results'" :class="['px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap', activeTab === 'results' ? 'text-indigo-400 border-indigo-400' : 'text-slate-400 border-transparent hover:text-slate-300']">
          Results ({{ processedCount }})
        </button>
        <button @click="activeTab = 'analytics'" :class="['px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap', activeTab === 'analytics' ? 'text-indigo-400 border-indigo-400' : 'text-slate-400 border-transparent hover:text-slate-300']">
          Analytics
        </button>
        <button @click="activeTab = 'critical'" :class="['px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap', activeTab === 'critical' ? 'text-red-400 border-red-400' : 'text-slate-400 border-transparent hover:text-slate-300']">
          Critical ({{ highPriorityCount }})
        </button>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 md:px-8 py-8">

      <!-- INBOX TAB -->
      <section v-show="activeTab === 'inbox'" class="space-y-6">
        <!-- Add Manual Message -->
        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <h3 class="text-sm font-semibold mb-4 text-slate-300">Add Manual Message</h3>
          <div class="space-y-3">
            <div>
              <textarea v-model="newMessageText" placeholder="Paste a message to analyze (min 5 chars)..." class="w-full bg-slate-900 border border-slate-700 text-slate-200 p-3 rounded-lg placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm" rows="3"></textarea>
              <p class="text-xs text-slate-500 mt-1">{{ newMessageText.length }}/2000 characters</p>
            </div>
            <div v-if="messageError" class="text-sm text-red-400 flex items-start gap-2 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
              <ExclamationTriangleIcon class="w-4 h-4 mt-0.5 flex-shrink-0" />
              {{ messageError }}
            </div>
            <div class="flex gap-3">
              <select v-model="newMessagePlatform" class="px-3 py-2 bg-slate-900 border border-slate-700 text-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm font-medium">
                <option>Manual</option>
                <option>Instagram</option>
                <option>Facebook</option>
                <option>Twitter</option>
                <option>LinkedIn</option>
                <option>DM</option>
              </select>
              <button @click="addManualMessage" :disabled="isAnalyzing" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2">
                <CheckCircleIcon class="w-4 h-4" /> Add
              </button>
            </div>
          </div>
        </div>

        <!-- Incoming Messages -->
        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
            <h2 class="text-lg font-semibold flex items-center gap-2 text-white">
              <ChatBubbleLeftEllipsisIcon class="w-5 h-5 text-slate-400" />
              Incoming Messages
              <span class="ml-auto bg-indigo-600 text-white text-xs px-2.5 py-1 rounded-full">{{ incomingMessages.length }}</span>
            </h2>
            <div class="flex gap-2 w-full md:w-auto flex-wrap">
              <select v-model="selectedPlatform" class="px-3 py-2 bg-slate-900 border border-slate-700 text-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm font-medium">
                <option>All</option>
                <option>Instagram</option>
                <option>Facebook</option>
                <option>Twitter</option>
                <option>LinkedIn</option>
                <option>DM</option>
                <option>Manual</option>
              </select>
              <button @click="refreshWithNewMessages" :disabled="isAnalyzing" class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg font-medium transition disabled:opacity-50 flex items-center gap-1.5 whitespace-nowrap">
                <ArrowPathIcon class="w-4 h-4" /> Refresh
              </button>
              <button v-if="filteredIncoming.length > 0" @click="batchTriage" :disabled="isAnalyzing" class="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm rounded-lg font-medium transition disabled:opacity-50 whitespace-nowrap">
                Analyze All
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="msg in filteredIncoming" :key="msg.id" class="bg-slate-800 p-5 rounded-lg border border-slate-600 hover:border-indigo-500/50 transition shadow-lg">
              <div class="flex justify-between items-start mb-3">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-900/50 px-2 py-1 rounded">{{ msg.platform }}</span>
                <span class="text-[10px] text-slate-500">ID: {{ msg.id }}</span>
              </div>
              <p class="text-slate-300 mb-4 text-sm leading-relaxed line-clamp-4">"{{ msg.text }}"</p>
              <button @click="triageMessage(msg)" :disabled="isAnalyzing" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg text-xs font-medium transition disabled:opacity-50 flex justify-center items-center gap-2">
                <SparklesIcon class="w-3.5 h-3.5" /> {{ isAnalyzing ? 'Processing...' : 'Analyze' }}
              </button>
            </div>

            <div v-if="filteredIncoming.length === 0" class="col-span-full text-center text-slate-500 py-12">
              <ChatBubbleLeftEllipsisIcon class="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p class="text-sm">No messages found for {{ selectedPlatform }}.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- RESULTS TAB -->
      <section v-show="activeTab === 'results'" class="space-y-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white flex items-center gap-2">
            <CheckCircleIcon class="w-5 h-5 text-emerald-400" />
            Processed Messages ({{ processedCount }})
          </h2>
          <button v-if="processedMessages.length > 0" @click="clearHistory" class="px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-xs rounded-lg font-medium transition border border-red-500/30 flex items-center gap-1">
            <TrashIcon class="w-3.5 h-3.5" /> Clear
          </button>
        </div>

        <div class="space-y-4">
          <div v-for="msg in processedMessages" :key="msg.id" class="bg-slate-800/40 p-6 rounded-xl border border-slate-700/50 hover:border-indigo-500/30 transition shadow-lg">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- Original Message -->
              <div class="lg:col-span-1">
                <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Original Message</h4>
                <p class="text-sm text-slate-300 leading-relaxed mb-3">"{{ msg.text }}"</p>
                <div class="text-xs text-slate-500 space-y-1">
                  <p><span class="text-slate-400 font-medium">Platform:</span> {{ msg.platform }}</p>
                  <p><span class="text-slate-400 font-medium">ID:</span> {{ msg.id }}</p>
                </div>
              </div>

              <!-- Analysis -->
              <div class="lg:col-span-1">
                <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">AI Analysis</h4>
                <div class="space-y-2">
                  <div :class="['px-3 py-2 rounded-lg text-xs font-semibold border', getUrgencyColor(msg.urgency)]">
                    {{ msg.urgency }} Urgency
                  </div>
                  <div class="text-xs bg-slate-700/50 px-3 py-2 rounded-lg border border-slate-600">
                    <span class="text-slate-400">Category:</span> {{ msg.category }}
                  </div>
                  <div class="text-xs bg-slate-700/50 px-3 py-2 rounded-lg border border-slate-600">
                    <span class="text-slate-400">Sentiment:</span> {{ msg.sentiment }}
                  </div>
                  <div class="text-xs bg-slate-700/50 px-3 py-2 rounded-lg border border-slate-600">
                    <span class="text-slate-400">Emotion:</span> {{ getEmotionIntensity(msg.emotion_score) }} ({{ msg.emotion_score }}/100)
                  </div>
                </div>
              </div>

              <!-- Suggested Reply -->
              <div class="lg:col-span-1">
                <h4 class="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <SparklesIcon class="w-3.5 h-3.5" /> AI Draft Response
                </h4>
                <p class="text-sm text-slate-200 leading-relaxed mb-4 bg-indigo-500/10 p-3 rounded-lg border border-indigo-500/20">
                  {{ msg.suggested_reply }}
                </p>
                <button class="w-full bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 text-xs px-3 py-2 rounded-lg font-semibold border border-emerald-500/20 transition flex items-center justify-center gap-1.5">
                  <CheckCircleIcon class="w-3.5 h-3.5" /> Approve & Send
                </button>
              </div>
            </div>
          </div>

          <div v-if="processedMessages.length === 0" class="flex flex-col items-center justify-center text-slate-500 py-20 border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-800/20">
            <CheckCircleIcon class="w-12 h-12 mb-4 opacity-20" />
            <p class="text-sm">No processed messages yet. Analyze some incoming messages to see results here.</p>
          </div>
        </div>
      </section>

      <!-- ANALYTICS TAB -->
      <section v-show="activeTab === 'analytics'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- KPI Cards -->
        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">Total Messages</p>
          <p class="text-3xl font-bold text-white">{{ analytics.total_messages || 0 }}</p>
        </div>

        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">High Priority</p>
          <p class="text-3xl font-bold text-red-400">{{ analytics.high_priority_count || 0 }}</p>
        </div>

        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">Avg Emotion Score</p>
          <p class="text-3xl font-bold text-indigo-400">{{ analytics.average_emotion_score || 0 }}</p>
        </div>

        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50">
          <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">AI Responses</p>
          <p class="text-3xl font-bold text-emerald-400">{{ analytics.ai_powered_responses || 0 }}</p>
        </div>

        <!-- Breakdown Tables -->
        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50 md:col-span-2">
          <h3 class="text-sm font-semibold text-white mb-4">By Urgency</h3>
          <div class="space-y-2">
            <div v-for="(count, urgency) in analytics.by_urgency" :key="urgency" class="flex justify-between text-sm">
              <span class="text-slate-400">{{ urgency }}</span>
              <span class="text-white font-semibold">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50 md:col-span-2">
          <h3 class="text-sm font-semibold text-white mb-4">By Platform</h3>
          <div class="space-y-2">
            <div v-for="(count, platform) in analytics.platforms" :key="platform" class="flex justify-between text-sm">
              <span class="text-slate-400">{{ platform }}</span>
              <span class="text-white font-semibold">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/40 rounded-xl p-6 border border-slate-700/50 lg:col-span-4">
          <h3 class="text-sm font-semibold text-white mb-4">By Category</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            <div v-for="(count, category) in analytics.by_category" :key="category" class="text-center">
              <p class="text-xs text-slate-400 mb-1">{{ category }}</p>
              <p class="text-2xl font-bold text-indigo-400">{{ count }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CRITICAL TAB -->
      <section v-show="activeTab === 'critical'" class="space-y-4">
        <h2 class="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <ShieldExclamationIcon class="w-5 h-5 text-red-400" />
          High Priority Messages ({{ highPriorityCount }})
        </h2>

        <div class="space-y-4">
          <div v-for="msg in highPriorityMessages" :key="msg.id" class="bg-red-500/10 p-6 rounded-xl border border-red-500/30 shadow-lg">
            <div class="flex items-start justify-between mb-4">
              <div>
                <p class="text-sm text-red-400 font-semibold mb-2">⚠️ URGENT - {{ msg.category }}</p>
                <p class="text-slate-200 leading-relaxed">"{{ msg.text }}"</p>
              </div>
              <span class="px-3 py-1 bg-red-500 text-white text-xs rounded-full font-bold">HIGH</span>
            </div>
            <p class="text-sm text-red-300 mb-3 italic">{{ msg.suggested_reply }}</p>
            <button class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm rounded-lg font-semibold transition">
              Take Action
            </button>
          </div>

          <div v-if="highPriorityMessages.length === 0" class="text-center text-slate-500 py-12">
            <ShieldExclamationIcon class="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p class="text-sm">No high-priority messages at the moment.</p>
          </div>
        </div>
      </section>

    </main>

  </div>
</template>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
