<template>
  <div class="test-execution">
    <div class="page-header">
      <h1>Execute Test Plan</h1>
    </div>

    <div class="content">
      <!-- Test Plan Selection -->
      <div class="selection-section">
        <div class="form-group">
          <label for="test-plan-select">Select Test Plan:</label>
          <select 
            id="test-plan-select"
            v-model="selectedTestPlan"
            class="form-select"
            :disabled="isExecuting"
          >
            <option value="">-- Select a test plan --</option>
            <option 
              v-for="testPlan in testPlans" 
              :key="testPlan.id" 
              :value="testPlan.id"
            >
              {{ testPlan.name }} ({{ testPlan.id }})
            </option>
          </select>
        </div>

        <button 
          @click="executeTestPlan"
          :disabled="!selectedTestPlan || isExecuting"
          class="btn btn-primary execute-btn"
        >
          {{ isExecuting ? 'Executing...' : 'Execute' }}
        </button>
      </div>

      <!-- Execution Status -->
      <div v-if="executionStatus" class="status-section">
        <div :class="['status-badge', executionStatus.toLowerCase()]">
          {{ executionStatus }}
        </div>
        <div class="status-message">{{ statusMessage }}</div>
      </div>

      <!-- Real-time Output -->
      <div v-if="output.length > 0" class="output-section">
        <div class="output-header">
          <h3>Execution Output</h3>
          <button 
            @click="clearOutput"
            class="btn btn-secondary btn-sm"
            :disabled="isExecuting"
          >
            Clear
          </button>
        </div>
        <div class="output-terminal" ref="outputTerminal">
          <div 
            v-for="(line, index) in output" 
            :key="index"
            :class="['output-line', line.stream]"
          >
            <span class="timestamp">{{ formatTimestamp(line.timestamp) }}</span>
            <span class="line-content">{{ line.line }}</span>
          </div>
        </div>
      </div>

      <!-- Execution Log Link -->
      <div v-if="executionLogLink" class="log-link-section">
        <div :class="['log-link', executionStatus === 'FAILED' ? 'log-link-failed' : 'log-link-success']">
          <h4>{{ executionStatus === 'FAILED' ? 'Execution Failed' : 'Execution Completed' }}</h4>
          <p>View detailed results:</p>
          <a 
            :href="executionLogLink.url" 
            target="_blank"
            :class="executionStatus === 'FAILED' ? 'btn btn-danger' : 'btn btn-success'"
          >
            View Execution Log: {{ executionLogLink.filename }}
          </a>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-section">
        <div class="error-message">
          <strong>Error:</strong> {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'TestExecution',
  setup() {
    const router = useRouter()
    const testPlans = ref([])
    const selectedTestPlan = ref('')
    const isExecuting = ref(false)
    const executionStatus = ref('')
    const statusMessage = ref('')
    const output = ref([])
    const executionLogLink = ref(null)
    const error = ref('')
    const websocket = ref(null)
    const outputTerminal = ref(null)

    const loadTestPlans = async () => {
      try {
        testPlans.value = await apiService.getTestPlans()
      } catch (err) {
        error.value = `Failed to load test plans: ${err.message}`
        console.error('Failed to load test plans:', err)
      }
    }

    const executeTestPlan = () => {
      if (!selectedTestPlan.value) return

      // Reset state
      isExecuting.value = true
      executionStatus.value = ''
      statusMessage.value = ''
      output.value = []
      executionLogLink.value = null
      error.value = ''

      // Connect to WebSocket
      connectWebSocket()
    }

    const connectWebSocket = () => {
      try {
        const wsUrl = 'ws://localhost:8000/ws/test-execution'
        websocket.value = new WebSocket(wsUrl)

        websocket.value.onopen = () => {
          console.log('WebSocket connected')
          // Send execution request
          websocket.value.send(JSON.stringify({
            test_plan_id: selectedTestPlan.value,
            debug_level: 0
          }))
        }

        websocket.value.onmessage = (event) => {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        }

        websocket.value.onerror = (error) => {
          console.error('WebSocket error:', error)
          error.value = 'WebSocket connection failed'
          isExecuting.value = false
        }

        websocket.value.onclose = () => {
          console.log('WebSocket disconnected')
          isExecuting.value = false
        }

      } catch (err) {
        error.value = `Failed to connect: ${err.message}`
        isExecuting.value = false
      }
    }

    const handleWebSocketMessage = (data) => {
      switch (data.type) {
        case 'STATUS':
          executionStatus.value = data.status
          statusMessage.value = data.message
          // Update execution state based on status
          if (data.status === 'COMPLETED' || data.status === 'FAILED') {
            isExecuting.value = false
          }
          break
        
        case 'OUTPUT':
          output.value.push({
            stream: data.stream,
            line: data.line,
            timestamp: data.timestamp
          })
          scrollToBottom()
          break
        
        case 'LOG_LINK':
          executionLogLink.value = {
            url: data.url,
            filename: data.filename
          }
          break
        
        case 'ERROR':
          error.value = data.message
          isExecuting.value = false
          break
      }
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (outputTerminal.value) {
          outputTerminal.value.scrollTop = outputTerminal.value.scrollHeight
        }
      })
    }

    const clearOutput = () => {
      output.value = []
    }

    const formatTimestamp = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString()
    }

    const cleanupWebSocket = () => {
      if (websocket.value) {
        websocket.value.close()
        websocket.value = null
      }
    }

    onMounted(() => {
      loadTestPlans()
    })

    onUnmounted(() => {
      cleanupWebSocket()
    })

    return {
      testPlans,
      selectedTestPlan,
      isExecuting,
      executionStatus,
      statusMessage,
      output,
      executionLogLink,
      error,
      outputTerminal,
      executeTestPlan,
      clearOutput,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.test-execution {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
}

.content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.selection-section {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
}

.form-select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.execute-btn {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  white-space: nowrap;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.status-badge.starting {
  background-color: #3498db;
  color: white;
}

.status-badge.running {
  background-color: #f39c12;
  color: white;
}

.status-badge.completed {
  background-color: #27ae60;
  color: white;
}

.status-badge.failed {
  background-color: #e74c3c;
  color: white;
}

.status-message {
  color: #7f8c8d;
  font-style: italic;
}

.output-section {
  margin-bottom: 2rem;
}

.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.output-header h3 {
  margin: 0;
  color: #2c3e50;
}

.output-terminal {
  background-color: #1e1e1e;
  color: #d4d4d4;
  border-radius: 4px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.output-line {
  margin-bottom: 0.25rem;
  display: flex;
  gap: 1rem;
}

.output-line.stdout {
  color: #d4d4d4;
}

.output-line.stderr {
  color: #f44747;
}

.timestamp {
  color: #6a9955;
  min-width: 80px;
}

.line-content {
  flex: 1;
}

.log-link-section {
  margin-top: 2rem;
  padding: 1.5rem;
  border-radius: 4px;
}

.log-link-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
}

.log-link-failed {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.log-link h4 {
  margin: 0 0 0.5rem 0;
}

.log-link-success h4 {
  color: #155724;
}

.log-link-failed h4 {
  color: #721c24;
}

.log-link p {
  margin: 0 0 1rem 0;
}

.log-link-success p {
  color: #155724;
}

.log-link-failed p {
  color: #721c24;
}

.error-section {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.error-message {
  color: #721c24;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.btn-success {
  background-color: #27ae60;
  color: white;
  text-decoration: none;
  display: inline-block;
  padding: 0.75rem 1.5rem;
}

.btn-success:hover {
  background-color: #219a52;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  text-decoration: none;
  display: inline-block;
  padding: 0.75rem 1.5rem;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}
</style>
