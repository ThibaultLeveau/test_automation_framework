<template>
  <div class="test-cases-table">
    <div class="table-header">
      <h3>Test Cases</h3>
      <div class="header-actions">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search test cases..."
            class="search-input"
          />
        </div>
        <button @click="addTestCase" class="btn btn-primary">
          + Add Test Case
        </button>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Steps</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="testCase in filteredTestCases" :key="testCase.id">
            <td>{{ testCase.id }}</td>
            <td>{{ testCase.name }}</td>
            <td>{{ testCase.description }}</td>
            <td>{{ testCase.steps ? testCase.steps.length : 0 }}</td>
            <td class="actions">
              <button 
                @click="editTestCase(testCase)" 
                class="btn btn-sm btn-secondary"
                title="Edit test case"
              >
                Edit
              </button>
              <button 
                @click="manageSteps(testCase)" 
                class="btn btn-sm btn-primary"
                title="Manage steps"
              >
                Steps
              </button>
              <button 
                @click="deleteTestCase(testCase.id)" 
                class="btn btn-sm btn-danger"
                title="Delete test case"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="filteredTestCases.length === 0">
            <td colspan="5" class="no-data">
              No test cases found. <a href="#" @click="addTestCase">Add one</a> to get started.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Test Case Editor Modal -->
    <div v-if="showTestCaseModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingTestCase ? 'Edit Test Case' : 'Add Test Case' }}</h3>
          <button @click="closeTestCaseModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="testCaseId">ID *</label>
            <input
              id="testCaseId"
              v-model="testCaseForm.id"
              type="number"
              :disabled="!!editingTestCase"
              :class="{ 'error': errors.id }"
            />
            <span v-if="errors.id" class="error-message">{{ errors.id }}</span>
          </div>
          <div class="form-group">
            <label for="testCaseName">Name *</label>
            <input
              id="testCaseName"
              v-model="testCaseForm.name"
              type="text"
              placeholder="Enter test case name"
              :class="{ 'error': errors.name }"
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>
          <div class="form-group">
            <label for="testCaseDescription">Description *</label>
            <textarea
              id="testCaseDescription"
              v-model="testCaseForm.description"
              placeholder="Enter test case description"
              rows="3"
              :class="{ 'error': errors.description }"
            ></textarea>
            <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeTestCaseModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveTestCase" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Steps Manager Modal -->
    <StepsTable
      v-if="showStepsModal"
      :test-case="selectedTestCase"
      :test-cases="testCases"
      @save="saveSteps"
      @close="closeStepsModal"
    />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import StepsTable from './StepsTable.vue'

export default {
  name: 'TestCasesTable',
  components: {
    StepsTable
  },
  props: {
    testCases: {
      type: Array,
      required: true
    }
  },
  emits: ['update:testCases'],
  setup(props, { emit }) {
    const searchQuery = ref('')
    const showTestCaseModal = ref(false)
    const showStepsModal = ref(false)
    const editingTestCase = ref(null)
    const selectedTestCase = ref(null)
    const saving = ref(false)
    
    const testCaseForm = ref({
      id: '',
      name: '',
      description: ''
    })
    
    const errors = ref({})

    // Filter test cases based on search query
    const filteredTestCases = computed(() => {
      if (!searchQuery.value.trim()) {
        return props.testCases
      }
      
      const query = searchQuery.value.toLowerCase()
      return props.testCases.filter(testCase => 
        testCase.name.toLowerCase().includes(query) ||
        testCase.description.toLowerCase().includes(query)
      )
    })

    // Generate next available ID
    const getNextId = () => {
      const ids = props.testCases.map(tc => tc.id)
      return ids.length > 0 ? Math.max(...ids) + 1 : 1
    }

    const addTestCase = () => {
      editingTestCase.value = null
      testCaseForm.value = {
        id: getNextId(),
        name: '',
        description: ''
      }
      errors.value = {}
      showTestCaseModal.value = true
    }

    const editTestCase = (testCase) => {
      editingTestCase.value = testCase
      testCaseForm.value = {
        id: testCase.id,
        name: testCase.name,
        description: testCase.description
      }
      errors.value = {}
      showTestCaseModal.value = true
    }

    const manageSteps = (testCase) => {
      selectedTestCase.value = testCase
      showStepsModal.value = true
    }

    const closeTestCaseModal = () => {
      showTestCaseModal.value = false
      editingTestCase.value = null
      testCaseForm.value = {
        id: '',
        name: '',
        description: ''
      }
      errors.value = {}
    }

    const closeStepsModal = () => {
      showStepsModal.value = false
      selectedTestCase.value = null
    }

    const validateTestCase = () => {
      errors.value = {}
      
      if (!testCaseForm.value.id || isNaN(testCaseForm.value.id)) {
        errors.value.id = 'ID must be a valid number'
      } else if (!editingTestCase.value) {
        // Check for duplicate ID when adding new
        const existingIds = props.testCases.map(tc => tc.id)
        if (existingIds.includes(parseInt(testCaseForm.value.id))) {
          errors.value.id = 'ID already exists'
        }
      }
      
      if (!testCaseForm.value.name.trim()) {
        errors.value.name = 'Name is required'
      }
      
      if (!testCaseForm.value.description.trim()) {
        errors.value.description = 'Description is required'
      }
      
      return Object.keys(errors.value).length === 0
    }

    const saveTestCase = () => {
      if (!validateTestCase()) {
        return
      }

      saving.value = true
      
      const testCaseData = {
        id: parseInt(testCaseForm.value.id),
        name: testCaseForm.value.name.trim(),
        description: testCaseForm.value.description.trim(),
        steps: editingTestCase.value ? editingTestCase.value.steps : []
      }

      let updatedTestCases
      if (editingTestCase.value) {
        // Update existing test case
        updatedTestCases = props.testCases.map(tc => 
          tc.id === editingTestCase.value.id ? testCaseData : tc
        )
      } else {
        // Add new test case
        updatedTestCases = [...props.testCases, testCaseData]
      }

      emit('update:testCases', updatedTestCases)
      saving.value = false
      closeTestCaseModal()
    }

    const deleteTestCase = (id) => {
      if (!confirm('Are you sure you want to delete this test case?')) {
        return
      }
      
      const updatedTestCases = props.testCases.filter(tc => tc.id !== id)
      emit('update:testCases', updatedTestCases)
    }

    const saveSteps = (testCaseId, steps) => {
      const updatedTestCases = props.testCases.map(tc => 
        tc.id === testCaseId ? { ...tc, steps } : tc
      )
      emit('update:testCases', updatedTestCases)
      closeStepsModal()
    }

    return {
      searchQuery,
      showTestCaseModal,
      showStepsModal,
      editingTestCase,
      selectedTestCase,
      saving,
      testCaseForm,
      errors,
      filteredTestCases,
      addTestCase,
      editTestCase,
      manageSteps,
      closeTestCaseModal,
      closeStepsModal,
      saveTestCase,
      deleteTestCase,
      saveSteps
    }
  }
}
</script>

<style scoped>
.test-cases-table {
  margin-bottom: 2rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 250px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
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

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.no-data {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
}

.no-data a {
  color: #3498db;
  text-decoration: none;
}

.no-data a:hover {
  text-decoration: underline;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.btn-close:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.form-group input,
.form-group textarea {
  width: 100%;
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

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

/* Responsive design */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .search-input {
    width: 200px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .modal {
    width: 95%;
    margin: 1rem;
  }
}
</style>
