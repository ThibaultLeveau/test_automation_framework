<template>
  <div class="test-plans">
    <div class="page-header">
      <h1>Test Plans</h1>
      <button @click="createNewTestPlan" class="btn btn-primary">
        New Test Plan
      </button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">Loading test plans...</div>
      
      <div v-else-if="error" class="error">
        <p>Error loading test plans: {{ error }}</p>
        <button @click="loadTestPlans" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else-if="testPlans.length === 0" class="empty-state">
        <p>No test plans found.</p>
        <button @click="createNewTestPlan" class="btn btn-primary">
          Create Your First Test Plan
        </button>
      </div>

      <div v-else class="test-plans-table">
        <table class="data-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Description</th>
              <th>Version</th>
              <th>Author</th>
              <th>Created Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="testPlan in testPlans" 
              :key="testPlan.id"
              @click="viewTestPlan(testPlan.id)"
              class="clickable-row"
            >
              <td>{{ getFileName(testPlan) }}</td>
              <td>{{ testPlan.description }}</td>
              <td>{{ testPlan.version }}</td>
              <td>{{ testPlan.author || 'Unknown' }}</td>
              <td>{{ testPlan.created_date || 'Unknown' }}</td>
              <td>
                <button 
                  @click.stop="deleteTestPlan(testPlan.id, testPlan.name)"
                  class="btn btn-danger btn-sm"
                  title="Delete test plan"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'TestPlans',
  setup() {
    const router = useRouter()
    const testPlans = ref([])
    const loading = ref(false)
    const error = ref(null)

    const loadTestPlans = async () => {
      loading.value = true
      error.value = null
      try {
        testPlans.value = await apiService.getTestPlans()
      } catch (err) {
        error.value = err.message
        console.error('Failed to load test plans:', err)
      } finally {
        loading.value = false
      }
    }

    const getFileName = (testPlan) => {
      return `${testPlan.id}.json`
    }

    const viewTestPlan = (id) => {
      router.push(`/test-plans/${id}`)
    }

    const createNewTestPlan = () => {
      router.push('/test-plans/new')
    }

    const deleteTestPlan = async (id, name) => {
      if (!confirm(`Are you sure you want to delete the test plan "${name}"?`)) {
        return
      }

      try {
        await apiService.deleteTestPlan(id)
        await loadTestPlans() // Reload the list
      } catch (err) {
        alert(`Failed to delete test plan: ${err.message}`)
      }
    }

    onMounted(() => {
      loadTestPlans()
    })

    return {
      testPlans,
      loading,
      error,
      loadTestPlans,
      getFileName,
      viewTestPlan,
      createNewTestPlan,
      deleteTestPlan
    }
  }
}
</script>

<style scoped>
.test-plans {
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

.content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
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
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-row:hover {
  background-color: #f8f9fa;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
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
</style>
