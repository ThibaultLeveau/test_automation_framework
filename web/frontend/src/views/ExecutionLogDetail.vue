<template>
  <div class="execution-log-detail">
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">
          ← Back to Logs
        </button>
        <h1>Execution Log Details</h1>
      </div>
      <div class="header-actions">
        <button @click="downloadJson" class="btn btn-primary">
          Download JSON
        </button>
      </div>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">Loading execution log...</div>
      
      <div v-else-if="error" class="error">
        <p>Error loading execution log: {{ error }}</p>
        <button @click="loadExecutionLog" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else-if="executionLog" class="log-content">
        <!-- Header Section -->
        <div class="log-header">
          <h2>{{ executionLog.test_plan_name || 'Unknown Test Plan' }}</h2>
          <div class="log-meta">
            <div class="meta-item">
              <strong>Timestamp:</strong> {{ formatTimestamp(executionLog.timestamp) }}
            </div>
            <div class="meta-item">
              <strong>User:</strong> {{ executionLog.current_user || 'N/A' }}
            </div>
            <div class="meta-item">
              <strong>Test Plan:</strong> {{ executionLog.test_plan_name || 'N/A' }}
            </div>
            <div class="meta-item">
              <strong>Command Line:</strong> {{ executionLog.command_line || 'N/A' }}
            </div>
            <div class="meta-item">
              <strong>Execution Time:</strong> {{ formatDuration(executionLog.execution_time_seconds) }}
            </div>
            <div class="meta-item">
              <strong>Status:</strong> 
              <span :class="['status-badge', getStatusClass(executionLog.results)]">
                {{ executionLog.results?.passed_steps || 0 }}/{{ executionLog.results?.total_steps || 0 }} - {{ Math.round(executionLog.results?.success_rate || 0) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Test Cases List -->
        <div class="test-cases-section">
          <h3>Test Cases</h3>
          <div class="test-cases-list">
            <div 
              v-for="testCase in groupedTestCases" 
              :key="testCase.name"
              class="test-case-item"
            >
              <div 
                class="test-case-header"
                @click="toggleTestCase(testCase.name)"
              >
                <div class="test-case-info">
                  <span class="test-case-name">{{ testCase.name }}</span>
                  <span :class="['test-case-status', testCase.status.toLowerCase()]">
                    {{ testCase.status }}
                  </span>
                </div>
                <div class="test-case-meta">
                  <span class="test-case-duration">{{ formatDuration(testCase.duration) }}</span>
                  <span class="test-case-steps">{{ testCase.steps.length }} steps</span>
                  <span class="expand-icon">{{ expandedTestCases[testCase.name] ? '▼' : '▶' }}</span>
                </div>
              </div>
              
              <div 
                v-if="expandedTestCases[testCase.name]" 
                class="test-case-steps-list"
              >
                <div 
                  v-for="step in testCase.steps" 
                  :key="`${testCase.name}-${step.step_number}`"
                  class="test-step-item"
                >
                  <div 
                    class="test-step-header"
                    @click="toggleTestStep(testCase.name, step.step_number)"
                  >
                    <div class="test-step-info">
                      <span class="test-step-number">Step {{ step.step_number }}</span>
                      <span :class="['test-step-status', step.status.toLowerCase()]">
                        {{ step.status }}
                      </span>
                    </div>
                    <div class="test-step-meta">
                      <span class="test-step-duration">{{ formatStepDuration(step) }}</span>
                      <span class="expand-icon">{{ expandedSteps[`${testCase.name}-${step.step_number}`] ? '▼' : '▶' }}</span>
                    </div>
                  </div>
                  
                  <div 
                    v-if="expandedSteps[`${testCase.name}-${step.step_number}`]" 
                    class="test-step-details"
                  >
                    <div v-if="step.stdout" class="detail-section">
                      <strong>STDOUT:</strong>
                      <pre class="output-text">{{ step.stdout }}</pre>
                    </div>
                    <div v-if="step.stderr" class="detail-section">
                      <strong>STDERR:</strong>
                      <pre class="output-text error-text">{{ step.stderr }}</pre>
                    </div>
                    <div v-if="step.exception" class="detail-section">
                      <strong>EXCEPTION:</strong>
                      <pre class="output-text error-text">{{ step.exception }}</pre>
                    </div>
                    <div v-if="!step.stdout && !step.stderr && !step.exception" class="detail-section">
                      <em>No output available</em>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'ExecutionLogDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const executionLog = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const expandedTestCases = ref({})
    const expandedSteps = ref({})

    const loadExecutionLog = async () => {
      loading.value = true
      error.value = null
      try {
        const filename = route.params.filename
        executionLog.value = await apiService.getExecutionLog(filename)
      } catch (err) {
        error.value = err.message
        console.error('Failed to load execution log:', err)
      } finally {
        loading.value = false
      }
    }

    const formattedJson = computed(() => {
      if (!executionLog.value) return ''
      return JSON.stringify(executionLog.value, null, 2)
    })

    // Group test cases and calculate durations
    const groupedTestCases = computed(() => {
      if (!executionLog.value?.detailed_results) return []

      const testCases = {}
      
      executionLog.value.detailed_results.forEach(step => {
        if (!testCases[step.test_case]) {
          testCases[step.test_case] = {
            name: step.test_case,
            steps: [],
            duration: 0
          }
        }
        testCases[step.test_case].steps.push(step)
      })

      // Calculate duration for each test case and determine status
      return Object.values(testCases).map(testCase => {
        // Sort steps by step number
        testCase.steps.sort((a, b) => a.step_number - b.step_number)
        
        // Calculate total duration for the test case
        if (testCase.steps.length > 1) {
          const firstStep = new Date(testCase.steps[0].timestamp)
          const lastStep = new Date(testCase.steps[testCase.steps.length - 1].timestamp)
          testCase.duration = (lastStep - firstStep) / 1000
        } else if (testCase.steps.length === 1) {
          testCase.duration = 0.1 // Default minimal duration for single step
        }

        // Determine test case status
        const hasFailed = testCase.steps.some(step => step.status === 'FAILED')
        testCase.status = hasFailed ? 'FAILED' : 'PASSED'

        return testCase
      })
    })

    const toggleTestCase = (testCaseName) => {
      expandedTestCases.value[testCaseName] = !expandedTestCases.value[testCaseName]
    }

    const toggleTestStep = (testCaseName, stepNumber) => {
      const key = `${testCaseName}-${stepNumber}`
      expandedSteps.value[key] = !expandedSteps.value[key]
    }

    const formatStepDuration = (step) => {
      // For individual steps, we'll use a default duration since we don't have exact step duration
      return '< 1s'
    }

    const goBack = () => {
      router.push('/execution-logs')
    }

    const downloadJson = () => {
      if (!executionLog.value) return

      const filename = route.params.filename
      const blob = new Blob([formattedJson.value], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const formatTimestamp = (timestamp) => {
      if (!timestamp) return 'N/A'
      try {
        const date = new Date(timestamp)
        return date.toLocaleString()
      } catch {
        return timestamp
      }
    }

    const formatDuration = (seconds) => {
      if (!seconds) return '0s'
      if (seconds < 60) return `${Math.round(seconds)}s`
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.round(seconds % 60)
      return `${minutes}m ${remainingSeconds}s`
    }

    const getStatusClass = (results) => {
      const successRate = results?.success_rate || 0
      return successRate === 100 ? 'success' : 'failed'
    }

    onMounted(() => {
      loadExecutionLog()
    })

    return {
      executionLog,
      loading,
      error,
      groupedTestCases,
      expandedTestCases,
      expandedSteps,
      toggleTestCase,
      toggleTestStep,
      formatStepDuration,
      goBack,
      downloadJson,
      formatTimestamp,
      formatDuration,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.execution-log-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #e74c3c;
}

.log-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.log-header h2 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.log-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-item strong {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
  display: inline-block;
}

.status-badge.success {
  background-color: #e8f6f3;
  color: #27ae60;
}

.status-badge.failed {
  background-color: #fdedec;
  color: #e74c3c;
}

/* Test Cases Section */
.test-cases-section {
  margin-top: 2rem;
}

.test-cases-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.test-cases-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.test-case-item {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.test-case-header:hover {
  background-color: #e9ecef;
}

.test-case-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.test-case-name {
  font-weight: 600;
  color: #2c3e50;
}

.test-case-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.test-case-status.passed {
  background-color: #e8f6f3;
  color: #27ae60;
}

.test-case-status.failed {
  background-color: #fdedec;
  color: #e74c3c;
}

.test-case-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.expand-icon {
  font-size: 0.8rem;
  color: #7f8c8d;
}

/* Test Steps List */
.test-case-steps-list {
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.test-step-item {
  border-bottom: 1px solid #e9ecef;
}

.test-step-item:last-child {
  border-bottom: none;
}

.test-step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.test-step-header:hover {
  background-color: #e9ecef;
}

.test-step-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.test-step-number {
  font-weight: 500;
  color: #2c3e50;
}

.test-step-status {
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.test-step-status.passed {
  background-color: #e8f6f3;
  color: #27ae60;
}

.test-step-status.failed {
  background-color: #fdedec;
  color: #e74c3c;
}

.test-step-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #7f8c8d;
  font-size: 0.85rem;
}

/* Test Step Details */
.test-step-details {
  padding: 1rem;
  background-color: white;
  border-top: 1px solid #e9ecef;
}

.detail-section {
  margin-bottom: 1rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 0.9rem;
}

.output-text {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 0.75rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.error-text {
  color: #e74c3c;
  background-color: #fdedec;
  border-color: #f5b7b1;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .log-meta {
    grid-template-columns: 1fr;
  }

  .test-case-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .test-case-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .test-case-meta {
    width: 100%;
    justify-content: space-between;
  }

  .test-step-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .test-step-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .test-step-meta {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
