<template>
  <div class="variables">
    <div class="page-header">
      <h1>Variables</h1>
      <button @click="createNewVariable" class="btn btn-primary">
        New Variable
      </button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">Loading variables...</div>
      
      <div v-else-if="error" class="error">
        <p>Error loading variables: {{ error }}</p>
        <button @click="loadVariables" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else-if="variables.length === 0" class="empty-state">
        <p>No variables found.</p>
        <button @click="createNewVariable" class="btn btn-primary">
          Create Your First Variable
        </button>
      </div>

      <div v-else class="variables-table">
        <table class="data-table">
          <thead>
            <tr>
              <th>Variable Name</th>
              <th>Value</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="variable in variables" 
              :key="variable.name"
            >
              <td>{{ variable.name }}</td>
              <td>{{ variable.value }}</td>
              <td>{{ variable.description || 'No description' }}</td>
              <td>
                <button 
                  @click="editVariable(variable)"
                  class="btn btn-secondary btn-sm"
                  title="Edit variable"
                >
                  Edit
                </button>
                <button 
                  @click="deleteVariable(variable.name, variable.name)"
                  class="btn btn-danger btn-sm"
                  title="Delete variable"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Variable Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ isEditing ? 'Edit Variable' : 'Create New Variable' }}</h2>
          <button @click="closeModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveVariable">
            <div class="form-group">
              <label for="variable-name">Variable Name</label>
              <input
                id="variable-name"
                v-model="currentVariable.name"
                type="text"
                required
                :disabled="isEditing"
                placeholder="Enter variable name (no spaces)"
                class="form-control"
              />
              <small class="form-text">Variable names must start with a letter or underscore and contain only alphanumeric characters and underscores.</small>
            </div>
            <div class="form-group">
              <label for="variable-value">Value</label>
              <input
                id="variable-value"
                v-model="currentVariable.value"
                type="text"
                required
                placeholder="Enter variable value"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label for="variable-description">Description</label>
              <textarea
                id="variable-description"
                v-model="currentVariable.description"
                placeholder="Enter variable description (optional)"
                class="form-control"
                rows="3"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary">
                {{ isEditing ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Variables',
  setup() {
    const variables = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showModal = ref(false)
    const isEditing = ref(false)
    const currentVariable = ref({
      name: '',
      value: '',
      description: ''
    })

    const loadVariables = async () => {
      loading.value = true
      error.value = null
      try {
        variables.value = await apiService.getVariables()
      } catch (err) {
        error.value = err.message
        console.error('Failed to load variables:', err)
      } finally {
        loading.value = false
      }
    }

    const createNewVariable = () => {
      currentVariable.value = {
        name: '',
        value: '',
        description: ''
      }
      isEditing.value = false
      showModal.value = true
    }

    const editVariable = (variable) => {
      currentVariable.value = { ...variable }
      isEditing.value = true
      showModal.value = true
    }

    const saveVariable = async () => {
      try {
        if (isEditing.value) {
          await apiService.updateVariable(currentVariable.value.name, currentVariable.value)
        } else {
          await apiService.createVariable(currentVariable.value)
        }
        await loadVariables()
        closeModal()
      } catch (err) {
        alert(`Failed to save variable: ${err.message}`)
      }
    }

    const deleteVariable = async (name, displayName) => {
      if (!confirm(`Are you sure you want to delete the variable "${displayName}"?`)) {
        return
      }

      try {
        await apiService.deleteVariable(name)
        await loadVariables()
      } catch (err) {
        alert(`Failed to delete variable: ${err.message}`)
      }
    }

    const closeModal = () => {
      showModal.value = false
      currentVariable.value = {
        name: '',
        value: '',
        description: ''
      }
    }

    onMounted(() => {
      loadVariables()
    })

    return {
      variables,
      loading,
      error,
      showModal,
      isEditing,
      currentVariable,
      loadVariables,
      createNewVariable,
      editVariable,
      saveVariable,
      deleteVariable,
      closeModal
    }
  }
}
</script>

<style scoped>
.variables {
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
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

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}

.form-control:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 2rem;
}
</style>
