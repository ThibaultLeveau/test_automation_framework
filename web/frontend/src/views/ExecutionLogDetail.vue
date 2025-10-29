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
        <button @click="copyToClipboard" class="btn btn-secondary">
          Copy JSON
        </button>
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
        <div class="log-header">
          <h2>{{ executionLog.test_plan_name || 'Unknown Test Plan' }}</h2>
          <div class="log-meta">
            <div class="meta-item">
              <strong>Execution ID:</strong> {{ executionLog.execution_id || 'N/A' }}
            </div>
            <div class="meta-item">
              <strong>Timestamp:</strong> {{ formatTimestamp(executionLog.timestamp) }}
            </div>
            <div class="meta-item">
              <strong>User:</strong> {{ executionLog.current_user || 'N/A' }}
            </div>
            <div class="meta-item">
              <strong>Duration:</strong> {{ formatDuration(executionLog.execution_time_seconds) }}
            </div>
            <div class="meta-item">
              <strong>Status:</strong> 
              <span :class="['status-badge', getStatusClass(executionLog.results)]">
                {{ Math.round(executionLog.results?.success_rate || 0) }}% Success
              </span>
            </div>
          </div>
        </div>

        <div class="json-viewer">
          <pre><code>{{ formattedJson }}</code></pre>
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

    const goBack = () => {
      router.push('/execution-logs')
    }

    const copyToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(formattedJson.value)
        alert('JSON copied to clipboard!')
      } catch (err) {
        console.error('Failed to copy to clipboard:', err)
        alert('Failed to copy JSON to clipboard')
      }
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
      formattedJson,
      goBack,
      copyToClipboard,
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

.json-viewer {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  overflow: auto;
  max-height: 70vh;
}

.json-viewer pre {
  margin: 0;
  padding: 1rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
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
}
</style>
