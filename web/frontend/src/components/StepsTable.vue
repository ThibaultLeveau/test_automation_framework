<template>
  <div class="modal-overlay">
    <div class="modal steps-modal">
      <div class="modal-header">
        <h3>Manage Steps for: {{ testCase.name }}</h3>
        <button @click="close" class="btn-close">×</button>
      </div>
      
      <div class="modal-body">
        <div class="table-header">
          <h4>Test Steps</h4>
          <div class="header-actions">
            <div class="search-box">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search steps..."
                class="search-input"
              />
            </div>
            <button @click="addStep" class="btn btn-primary">
              + Add Step
            </button>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Step #</th>
                <th>Script</th>
                <th>Function</th>
                <th>Parameters</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="step in filteredSteps" :key="step.step_number">
                <td>{{ step.step_number }}</td>
                <td>{{ step.test_script }}</td>
                <td>{{ step.test_function }}</td>
                <td>
                  <div class="parameters-preview">
                    <template v-if="step.parameters && Object.keys(step.parameters).length > 0">
                      <span 
                        v-for="(value, key) in step.parameters" 
                        :key="key"
                        class="parameter-tag"
                        :title="`${key}: ${value}`"
                      >
                        {{ key }}
                      </span>
                    </template>
                    <span v-else class="no-parameters">No parameters</span>
                  </div>
                </td>
                <td class="actions">
                  <button 
                    @click="editStep(step)" 
                    class="btn btn-sm btn-secondary"
                    title="Edit step"
                  >
                    Edit
                  </button>
                  <button 
                    @click="moveStep(step.step_number, -1)" 
                    class="btn btn-sm btn-outline"
                    :disabled="step.step_number === 1"
                    title="Move up"
                  >
                    ↑
                  </button>
                  <button 
                    @click="moveStep(step.step_number, 1)" 
                    class="btn btn-sm btn-outline"
                    :disabled="step.step_number === steps.length"
                    title="Move down"
                  >
                    ↓
                  </button>
                  <button 
                    @click="deleteStep(step.step_number)" 
                    class="btn btn-sm btn-danger"
                    title="Delete step"
                  >
                    Delete
                  </button>
                </td>
              </tr>
              <tr v-if="filteredSteps.length === 0">
                <td colspan="5" class="no-data">
                  No steps found. <a href="#" @click="addStep">Add one</a> to get started.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="close" class="btn btn-secondary">Cancel</button>
        <button @click="save" class="btn btn-primary">Save Steps</button>
      </div>

      <!-- Step Editor Modal -->
      <StepEditorModal
        v-if="showStepModal"
        :step="editingStep"
        :step-number="editingStepNumber"
        :script-catalog="scriptCatalog"
        @save="saveStep"
        @close="closeStepModal"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import StepEditorModal from './StepEditorModal.vue'
import apiService from '../services/api.js'

export default {
  name: 'StepsTable',
  components: {
    StepEditorModal
  },
  props: {
    testCase: {
      type: Object,
      required: true
    }
  },
  emits: ['save', 'close'],
  setup(props, { emit }) {
    const steps = ref([])
    const scriptCatalog = ref([])
    const searchQuery = ref('')
    const showStepModal = ref(false)
    const editingStep = ref(null)
    const editingStepNumber = ref(null)

    // Initialize steps from test case
    onMounted(async () => {
      steps.value = props.testCase.steps ? [...props.testCase.steps] : []
      await loadScriptCatalog()
    })

    // Load script catalog from API
    const loadScriptCatalog = async () => {
      try {
        const catalog = await apiService.getTestCatalog()
        scriptCatalog.value = catalog.scripts || []
      } catch (error) {
        console.error('Failed to load script catalog:', error)
      }
    }

    // Filter steps based on search query
    const filteredSteps = computed(() => {
      if (!searchQuery.value.trim()) {
        return steps.value
      }
      
      const query = searchQuery.value.toLowerCase()
      return steps.value.filter(step => 
        step.test_script.toLowerCase().includes(query) ||
        step.test_function.toLowerCase().includes(query) ||
        JSON.stringify(step.parameters).toLowerCase().includes(query)
      )
    })

    const addStep = () => {
      editingStep.value = null
      editingStepNumber.value = steps.value.length + 1
      showStepModal.value = true
    }

    const editStep = (step) => {
      editingStep.value = { ...step }
      editingStepNumber.value = step.step_number
      showStepModal.value = true
    }

    const closeStepModal = () => {
      showStepModal.value = false
      editingStep.value = null
      editingStepNumber.value = null
    }

    const saveStep = (stepData) => {
      if (editingStep.value) {
        // Update existing step
        const index = steps.value.findIndex(s => s.step_number === editingStepNumber.value)
        if (index !== -1) {
          steps.value[index] = { ...stepData, step_number: editingStepNumber.value }
        }
      } else {
        // Add new step
        steps.value.push({ ...stepData, step_number: editingStepNumber.value })
      }
      
      // Reorder steps to ensure sequential step numbers
      reorderSteps()
      closeStepModal()
    }

    const deleteStep = (stepNumber) => {
      if (!confirm('Are you sure you want to delete this step?')) {
        return
      }
      
      steps.value = steps.value.filter(step => step.step_number !== stepNumber)
      reorderSteps()
    }

    const moveStep = (stepNumber, direction) => {
      const index = steps.value.findIndex(step => step.step_number === stepNumber)
      if (index === -1) return

      const newIndex = index + direction
      if (newIndex < 0 || newIndex >= steps.value.length) return

      // Swap steps
      [steps.value[index], steps.value[newIndex]] = [steps.value[newIndex], steps.value[index]]
      
      // Reorder steps to ensure sequential step numbers
      reorderSteps()
    }

    const reorderSteps = () => {
      steps.value = steps.value.map((step, index) => ({
        ...step,
        step_number: index + 1
      }))
    }

    const save = () => {
      emit('save', props.testCase.id, steps.value)
    }

    const close = () => {
      emit('close')
    }

    return {
      steps,
      scriptCatalog,
      searchQuery,
      showStepModal,
      editingStep,
      editingStepNumber,
      filteredSteps,
      addStep,
      editStep,
      closeStepModal,
      saveStep,
      deleteStep,
      moveStep,
      save,
      close
    }
  }
}
</script>

<style scoped>
.steps-modal {
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
}

.modal-body {
  padding: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #ecf0f1;
}

.table-header h4 {
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
  width: 200px;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
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
  position: sticky;
  top: 0;
}

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.parameters-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  max-width: 200px;
}

.parameter-tag {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80px;
}

.no-parameters {
  color: #6c757d;
  font-style: italic;
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 0.25rem;
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

.btn-outline {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f8f9fa;
  border-color: #adb5bd;
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

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .steps-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .search-input {
    width: 150px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .parameters-preview {
    max-width: 120px;
  }
  
  .parameter-tag {
    max-width: 60px;
  }
}
</style>
