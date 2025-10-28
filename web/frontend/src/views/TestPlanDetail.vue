<template>
  <div class="test-plan-detail">
    <div class="page-header">
      <button @click="goBack" class="btn btn-secondary">
        ← Back to Test Plans
      </button>
      <h1>{{ isNew ? 'Create New Test Plan' : `Edit Test Plan: ${testPlan.name}` }}</h1>
      <div class="actions">
        <button @click="saveTestPlan" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
        <button 
          v-if="!isNew" 
          @click="deleteTestPlan" 
          class="btn btn-danger"
          :disabled="saving"
        >
          Delete
        </button>
      </div>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">Loading test plan...</div>
      
      <div v-else-if="error" class="error">
        <p>Error: {{ error }}</p>
        <button @click="loadTestPlan" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else class="form-container">
        <div class="form-section">
          <h2>Basic Information</h2>
          <div class="form-grid">
            <div class="form-group">
              <label for="name">Name *</label>
              <input
                id="name"
                v-model="testPlan.name"
                type="text"
                placeholder="Enter test plan name"
                :class="{ 'error': errors.name }"
              />
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="description">Description *</label>
              <textarea
                id="description"
                v-model="testPlan.description"
                placeholder="Enter test plan description"
                rows="3"
                :class="{ 'error': errors.description }"
              ></textarea>
              <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
            </div>

            <div class="form-group">
              <label for="version">Version</label>
              <input
                id="version"
                v-model="testPlan.version"
                type="text"
                placeholder="1.0.0"
              />
            </div>

            <div class="form-group">
              <label for="author">Author</label>
              <input
                id="author"
                v-model="testPlan.author"
                type="text"
                placeholder="Enter author name"
              />
            </div>

            <div class="form-group" v-if="!isNew">
              <label>Created Date</label>
              <input
                :value="testPlan.created_date"
                type="text"
                disabled
                class="disabled"
              />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2>Test Cases</h2>
          <div class="form-group">
            <label for="testCases">Test Cases (JSON Format) *</label>
            <textarea
              id="testCases"
              v-model="testCasesJson"
              placeholder='[{"id": 1, "name": "Test Case 1", "steps": []}]'
              rows="15"
              :class="{ 'error': errors.test_cases }"
              @input="validateJson"
            ></textarea>
            <span v-if="errors.test_cases" class="error-message">{{ errors.test_cases }}</span>
            <div v-if="jsonValid" class="success-message">✓ Valid JSON</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'TestPlanDetail',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const testPlanId = route.params.id
    const isNew = computed(() => testPlanId === 'new')
    
    const testPlan = ref({
      name: '',
      description: '',
      version: '1.0.0',
      author: 'Unknown',
      created_date: null,
      test_cases: []
    })
    
    const testCasesJson = ref('[]')
    const loading = ref(false)
    const saving = ref(false)
    const error = ref(null)
    const jsonValid = ref(true)
    const errors = ref({})

    const loadTestPlan = async () => {
      if (isNew.value) return
      
      loading.value = true
      error.value = null
      try {
        const data = await apiService.getTestPlan(testPlanId)
        testPlan.value = data
        testCasesJson.value = JSON.stringify(data.test_cases, null, 2)
      } catch (err) {
        error.value = err.message
        console.error('Failed to load test plan:', err)
      } finally {
        loading.value = false
      }
    }

    const validateJson = () => {
      try {
        JSON.parse(testCasesJson.value)
        jsonValid.value = true
        errors.value.test_cases = null
      } catch (err) {
        jsonValid.value = false
        errors.value.test_cases = 'Invalid JSON format'
      }
    }

    const validateForm = () => {
      errors.value = {}
      
      if (!testPlan.value.name.trim()) {
        errors.value.name = 'Name is required'
      }
      
      if (!testPlan.value.description.trim()) {
        errors.value.description = 'Description is required'
      }
      
      if (!jsonValid.value) {
        errors.value.test_cases = 'Test cases must be valid JSON'
      }
      
      return Object.keys(errors.value).length === 0
    }

    const saveTestPlan = async () => {
      if (!validateForm()) {
        return
      }

      saving.value = true
      try {
        const testPlanData = {
          ...testPlan.value,
          test_cases: JSON.parse(testCasesJson.value)
        }

        if (isNew.value) {
          await apiService.createTestPlan(testPlanData)
        } else {
          await apiService.updateTestPlan(testPlanId, testPlanData)
        }
        
        router.push('/test-plans')
      } catch (err) {
        alert(`Failed to save test plan: ${err.message}`)
      } finally {
        saving.value = false
      }
    }

    const deleteTestPlan = async () => {
      if (!confirm(`Are you sure you want to delete the test plan "${testPlan.value.name}"?`)) {
        return
      }

      try {
        await apiService.deleteTestPlan(testPlanId)
        router.push('/test-plans')
      } catch (err) {
        alert(`Failed to delete test plan: ${err.message}`)
      }
    }

    const goBack = () => {
      router.push('/test-plans')
    }

    onMounted(() => {
      loadTestPlan()
    })

    return {
      testPlan,
      testCasesJson,
      loading,
      saving,
      error,
      jsonValid,
      errors,
      isNew,
      loadTestPlan,
      validateJson,
      saveTestPlan,
      deleteTestPlan,
      goBack
    }
  }
}
</script>

<style scoped>
.test-plan-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
  flex: 1;
  text-align: center;
}

.actions {
  display: flex;
  gap: 0.5rem;
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

.form-section {
  margin-bottom: 2rem;
}

.form-section h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 0.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-group input.error,
.form-group textarea.error {
  border-color: #e74c3c;
}

.form-group input.disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.success-message {
  color: #27ae60;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
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

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .actions {
    justify-content: center;
  }
}
</style>
