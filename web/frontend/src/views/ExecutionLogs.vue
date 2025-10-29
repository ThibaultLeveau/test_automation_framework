<template>
  <div class="execution-logs">
    <div class="page-header">
      <h1>Execution Logs</h1>
      <div class="header-actions">
        <button 
          v-if="selectedLogs.length > 0" 
          @click="deleteSelectedLogs" 
          class="btn btn-danger"
        >
          Delete Selected ({{ selectedLogs.length }})
        </button>
      </div>
    </div>

    <div class="content">
      <div class="filters">
        <div class="filter-group">
          <label for="test-plan-filter">Test Plan:</label>
          <input
            id="test-plan-filter"
            v-model="filters.testPlanName"
            type="text"
            placeholder="Filter by test plan name..."
            class="form-control"
          />
        </div>
        <div class="filter-group">
          <label for="date-filter">Date:</label>
          <input
            id="date-filter"
            v-model="filters.executionDate"
            type="date"
            class="form-control"
          />
        </div>
        <div class="filter-group">
          <label for="status-filter">Status:</label>
          <select
            id="status-filter"
            v-model="filters.status"
            class="form-control"
          >
            <option value="">All</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading">Loading execution logs...</div>
      
      <div v-else-if="error" class="error">
        <p>Error loading execution logs: {{ error }}</p>
        <button @click="loadExecutionLogs" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else-if="filteredLogs.length === 0" class="empty-state">
        <p v-if="executionLogs.length === 0">No execution logs found.</p>
        <p v-else>No execution logs match your filters.</p>
      </div>

      <div v-else class="execution-logs-table">
        <table class="data-table">
          <thead>
            <tr>
              <th class="select-column">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th @click="sortBy('test_plan_name')" class="sortable">
                Test Plan Name
                <span v-if="sortField === 'test_plan_name'" class="sort-indicator">
                  {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="sortBy('execution_date')" class="sortable">
                Execution Date
                <span v-if="sortField === 'execution_date'" class="sort-indicator">
                  {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="sortBy('execution_time')" class="sortable">
                Time
                <span v-if="sortField === 'execution_time'" class="sort-indicator">
                  {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>Duration</th>
              <th>Success Rate</th>
              <th>Total Steps</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="log in filteredLogs" 
              :key="log.filename"
              :class="{ 'selected': selectedLogs.includes(log.filename) }"
            >
              <td class="select-column">
                <input
                  type="checkbox"
                  :checked="selectedLogs.includes(log.filename)"
                  @change="toggleSelectLog(log.filename)"
                />
              </td>
              <td class="test-plan-name">{{ log.test_plan_name }}</td>
              <td>{{ log.execution_date }}</td>
              <td>{{ log.execution_time }}</td>
              <td>{{ formatDuration(log.execution_time_seconds) }}</td>
              <td>
                <span 
                  :class="['status-badge', getStatusClass(log.results)]"
                  :title="`${log.results.passed_steps || 0}/${log.results.total_steps || 0} steps passed`"
                >
                  {{ Math.round(log.results.success_rate || 0) }}%
                </span>
              </td>
              <td>{{ log.results.total_steps || 0 }}</td>
              <td>
                <button 
                  @click="viewLogDetails(log.filename)"
                  class="btn btn-secondary btn-sm"
                  title="View details"
                >
                  View
                </button>
                <button 
                  @click="deleteLog(log.filename, log.test_plan_name)"
                  class="btn btn-danger btn-sm"
                  title="Delete log"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'ExecutionLogs',
  setup() {
    const router = useRouter()
    const executionLogs = ref([])
    const loading = ref(false)
    const error = ref(null)
    const selectedLogs = ref([])
    const sortField = ref('execution_date')
    const sortDirection = ref('desc')
    
    const filters = ref({
      testPlanName: '',
      executionDate: '',
      status: ''
    })

    const loadExecutionLogs = async () => {
      loading.value = true
      error.value = null
      try {
        executionLogs.value = await apiService.getExecutionLogs()
      } catch (err) {
        error.value = err.message
        console.error('Failed to load execution logs:', err)
      } finally {
        loading.value = false
      }
    }

    const filteredLogs = computed(() => {
      let filtered = executionLogs.value.filter(log => {
        const matchesTestPlan = log.test_plan_name.toLowerCase().includes(filters.value.testPlanName.toLowerCase())
        const matchesDate = !filters.value.executionDate || log.execution_date === filters.value.executionDate
        const matchesStatus = !filters.value.status || getStatusClass(log.results) === filters.value.status
        
        return matchesTestPlan && matchesDate && matchesStatus
      })

      // Sort the filtered results
      filtered.sort((a, b) => {
        let aValue = a[sortField.value]
        let bValue = b[sortField.value]
        
        // Handle nested properties for results
        if (sortField.value === 'success_rate') {
          aValue = a.results?.success_rate || 0
          bValue = b.results?.success_rate || 0
        }
        
        if (sortDirection.value === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
        } else {
          return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
        }
      })

      return filtered
    })

    const allSelected = computed(() => {
      return filteredLogs.value.length > 0 && 
             filteredLogs.value.every(log => selectedLogs.value.includes(log.filename))
    })

    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortDirection.value = 'asc'
      }
    }

    const toggleSelectAll = () => {
      if (allSelected.value) {
        // Deselect all
        selectedLogs.value = selectedLogs.value.filter(filename => 
          !filteredLogs.value.some(log => log.filename === filename)
        )
      } else {
        // Select all visible
        const visibleFilenames = filteredLogs.value.map(log => log.filename)
        selectedLogs.value = [...new Set([...selectedLogs.value, ...visibleFilenames])]
      }
    }

    const toggleSelectLog = (filename) => {
      const index = selectedLogs.value.indexOf(filename)
      if (index > -1) {
        selectedLogs.value.splice(index, 1)
      } else {
        selectedLogs.value.push(filename)
      }
    }

    const viewLogDetails = (filename) => {
      router.push(`/execution-logs/${filename}`)
    }

    const deleteLog = async (filename, testPlanName) => {
      if (!confirm(`Are you sure you want to delete the execution log for "${testPlanName}"?`)) {
        return
      }

      try {
        await apiService.deleteExecutionLog(filename)
        await loadExecutionLogs()
        // Remove from selected logs if it was selected
        const index = selectedLogs.value.indexOf(filename)
        if (index > -1) {
          selectedLogs.value.splice(index, 1)
        }
      } catch (err) {
        alert(`Failed to delete execution log: ${err.message}`)
      }
    }

    const deleteSelectedLogs = async () => {
      if (!confirm(`Are you sure you want to delete ${selectedLogs.value.length} execution logs?`)) {
        return
      }

      try {
        await apiService.deleteExecutionLogs(selectedLogs.value)
        await loadExecutionLogs()
        selectedLogs.value = []
      } catch (err) {
        alert(`Failed to delete execution logs: ${err.message}`)
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
      loadExecutionLogs()
    })

    return {
      executionLogs,
      loading,
      error,
      selectedLogs,
      filters,
      filteredLogs,
      allSelected,
      sortField,
      sortDirection,
      loadExecutionLogs,
      sortBy,
      toggleSelectAll,
      toggleSelectLog,
      viewLogDetails,
      deleteLog,
      deleteSelectedLogs,
      formatDuration,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.execution-logs {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
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

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #e74c3c;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  position: relative;
}

.select-column {
  width: 40px;
  text-align: center;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #e8f4fd;
}

.sort-indicator {
  margin-left: 0.5rem;
  font-weight: bold;
}

.test-plan-name {
  font-weight: 600;
  color: #2c3e50;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.success {
  background-color: #e8f6f3;
  color: #27ae60;
}

.status-badge.failed {
  background-color: #fdedec;
  color: #e74c3c;
}

tr.selected {
  background-color: #e8f4fd;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  margin-right: 0.5rem;
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

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state p {
  margin-bottom: 1rem;
  color: #7f8c8d;
}

.form-control {
  padding: 0.5rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}
</style>
