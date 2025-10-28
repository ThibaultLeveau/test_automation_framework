<template>
  <div class="modal-overlay">
    <div class="modal step-editor-modal">
      <div class="modal-header">
        <h3>{{ step ? 'Edit Step' : 'Add Step' }} {{ stepNumber ? `#${stepNumber}` : '' }}</h3>
        <button @click="close" class="btn-close">×</button>
      </div>
      
      <div class="modal-body">
        <div class="form-section">
          <h4>Script Selection</h4>
          <div class="form-grid">
            <div class="form-group">
              <label for="scriptCategory">Category</label>
              <select
                id="scriptCategory"
                v-model="selectedCategory"
                class="form-select"
              >
                <option value="">All Categories</option>
                <option 
                  v-for="category in categories" 
                  :key="category"
                  :value="category"
                >
                  {{ category }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="testScript">Test Script *</label>
              <select
                id="testScript"
                v-model="selectedScript"
                class="form-select"
                :class="{ 'error': errors.test_script }"
              >
                <option value="">Select a script...</option>
                <option 
                  v-for="script in filteredScripts" 
                  :key="script.script_path"
                  :value="script.script_path"
                >
                  {{ script.script_path }}
                </option>
              </select>
              <span v-if="errors.test_script" class="error-message">{{ errors.test_script }}</span>
            </div>

            <div class="form-group">
              <label for="testFunction">Test Function *</label>
              <select
                id="testFunction"
                v-model="selectedFunction"
                class="form-select"
                :class="{ 'error': errors.test_function }"
                :disabled="!selectedScript"
              >
                <option value="">Select a function...</option>
                <option 
                  v-for="func in availableFunctions" 
                  :key="func.function_name"
                  :value="func.function_name"
                >
                  {{ func.function_name }}
                </option>
              </select>
              <span v-if="errors.test_function" class="error-message">{{ errors.test_function }}</span>
            </div>
          </div>
        </div>

        <div v-if="selectedFunctionData" class="form-section">
          <h4>Function Details</h4>
          <div class="function-info">
            <p><strong>Description:</strong> {{ selectedFunctionData.description }}</p>
            <p><strong>Platform Support:</strong> {{ selectedFunctionData.platform_support.join(', ') }}</p>
          </div>
        </div>

        <div v-if="selectedFunctionData" class="form-section">
          <h4>Parameters</h4>
          <div class="parameters-grid">
            <div 
              v-for="(paramInfo, paramName) in selectedFunctionData.function_args" 
              :key="paramName"
              class="form-group"
            >
              <label :for="paramName">
                {{ paramName }}
                <span v-if="isRequiredParameter(paramInfo)" class="required">*</span>
                <span class="parameter-type">({{ getParameterType(paramInfo) }})</span>
              </label>
              <input
                :id="paramName"
                v-model="parameters[paramName]"
                type="text"
                :placeholder="getParameterPlaceholder(paramInfo)"
                :class="{ 'error': errors[paramName] }"
              />
              <span class="parameter-description">{{ getParameterDescription(paramInfo) }}</span>
              <span v-if="errors[paramName]" class="error-message">{{ errors[paramName] }}</span>
            </div>
          </div>
        </div>

        <div v-if="!selectedFunctionData && (selectedScript || selectedFunction)" class="form-section">
          <div class="no-function-info">
            <p>Select a script and function to configure parameters.</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="close" class="btn btn-secondary">Cancel</button>
        <button @click="save" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'StepEditorModal',
  props: {
    step: {
      type: Object,
      default: null
    },
    stepNumber: {
      type: Number,
      default: null
    },
    scriptCatalog: {
      type: Array,
      required: true
    }
  },
  emits: ['save', 'close'],
  setup(props, { emit }) {
    const selectedCategory = ref('')
    const selectedScript = ref('')
    const selectedFunction = ref('')
    const parameters = ref({})
    const saving = ref(false)
    const errors = ref({})

    // Initialize form if editing existing step
    if (props.step) {
      selectedScript.value = props.step.test_script
      selectedFunction.value = props.step.test_function
      parameters.value = { ...(props.step.parameters || {}) }
    }

    // Get unique categories from script catalog
    const categories = computed(() => {
      const uniqueCategories = new Set()
      props.scriptCatalog.forEach(script => {
        if (script.category) {
          uniqueCategories.add(script.category)
        }
      })
      return Array.from(uniqueCategories).sort()
    })

    // Filter scripts by selected category
    const filteredScripts = computed(() => {
      if (!selectedCategory.value) {
        return props.scriptCatalog
      }
      return props.scriptCatalog.filter(script => script.category === selectedCategory.value)
    })

    // Get available functions for selected script
    const availableFunctions = computed(() => {
      if (!selectedScript.value) {
        return []
      }
      
      // Group functions by script path
      const functionsByScript = {}
      props.scriptCatalog.forEach(script => {
        if (!functionsByScript[script.script_path]) {
          functionsByScript[script.script_path] = []
        }
        functionsByScript[script.script_path].push(script)
      })
      
      return functionsByScript[selectedScript.value] || []
    })

    // Get data for selected function
    const selectedFunctionData = computed(() => {
      if (!selectedScript.value || !selectedFunction.value) {
        return null
      }
      
      return props.scriptCatalog.find(script => 
        script.script_path === selectedScript.value && 
        script.function_name === selectedFunction.value
      )
    })

    // Watch for script changes to reset function selection
    watch(selectedScript, (newScript) => {
      if (newScript !== props.step?.test_script) {
        selectedFunction.value = ''
        parameters.value = {}
      }
    })

    // Watch for function changes to reset parameters
    watch(selectedFunction, (newFunction) => {
      if (newFunction !== props.step?.test_function) {
        parameters.value = {}
      }
    })

    // Helper functions for parameter parsing
    const isRequiredParameter = (paramInfo) => {
      return paramInfo.includes('(required)')
    }

    const getParameterType = (paramInfo) => {
      const match = paramInfo.match(/^([^(]+)/)
      return match ? match[1].trim() : 'unknown'
    }

    const getParameterDescription = (paramInfo) => {
      const match = paramInfo.match(/-\s*(.+)$/)
      return match ? match[1] : paramInfo
    }

    const getParameterPlaceholder = (paramInfo) => {
      const type = getParameterType(paramInfo)
      if (type.includes('bool')) {
        return 'true or false'
      } else if (type.includes('int')) {
        return 'Enter a number'
      } else if (type.includes('str')) {
        return 'Enter text'
      } else if (type.includes('dict')) {
        return 'JSON object or key=value pairs'
      } else if (type.includes('list')) {
        return 'Comma-separated values'
      }
      return 'Enter value'
    }

    const validateForm = () => {
      errors.value = {}
      
      if (!selectedScript.value) {
        errors.value.test_script = 'Test script is required'
      }
      
      if (!selectedFunction.value) {
        errors.value.test_function = 'Test function is required'
      }
      
      // Validate required parameters
      if (selectedFunctionData.value) {
        for (const [paramName, paramInfo] of Object.entries(selectedFunctionData.value.function_args)) {
          if (isRequiredParameter(paramInfo) && (!parameters.value[paramName] || parameters.value[paramName].toString().trim() === '')) {
            errors.value[paramName] = `${paramName} is required`
          }
        }
      }
      
      return Object.keys(errors.value).length === 0
    }

    const save = () => {
      if (!validateForm()) {
        return
      }

      saving.value = true
      
      const stepData = {
        test_script: selectedScript.value,
        test_function: selectedFunction.value,
        parameters: { ...parameters.value }
      }

      // Clean up parameters - remove empty values
      Object.keys(stepData.parameters).forEach(key => {
        if (stepData.parameters[key] === '' || stepData.parameters[key] == null) {
          delete stepData.parameters[key]
        }
      })

      emit('save', stepData)
      saving.value = false
    }

    const close = () => {
      emit('close')
    }

    return {
      selectedCategory,
      selectedScript,
      selectedFunction,
      parameters,
      saving,
      errors,
      categories,
      filteredScripts,
      availableFunctions,
      selectedFunctionData,
      isRequiredParameter,
      getParameterType,
      getParameterDescription,
      getParameterPlaceholder,
      save,
      close
    }
  }
}
</script>

<style scoped>
.step-editor-modal {
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
}

.modal-body {
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
  border-bottom: 1px solid #ecf0f1;
  padding-bottom: 0.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.parameters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.required {
  color: #e74c3c;
}

.parameter-type {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: normal;
}

.parameter-description {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.25rem;
  line-height: 1.3;
}

.form-select,
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-select:focus,
.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.form-select.error,
.form-group input.error {
  border-color: #e74c3c;
}

.form-select:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.function-info {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.function-info p {
  margin: 0.5rem 0;
  line-height: 1.4;
}

.no-function-info {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
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
  z-index: 1001;
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

/* Responsive design */
@media (max-width: 768px) {
  .step-editor-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .parameters-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-body {
    padding: 1rem;
  }
}
</style>
