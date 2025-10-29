<template>
  <div class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Test Function' : 'Create New Test Function' }}</h2>
        <button @click="cancel" class="btn-close" title="Close">×</button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="save">
          <div class="form-group">
            <label for="script_path">Script Path *</label>
            <input
              id="script_path"
              v-model="formData.script_path"
              type="text"
              required
              placeholder="e.g., files/check_files.py"
            />
          </div>

          <div class="form-group">
            <label for="function_name">Function Name *</label>
            <input
              id="function_name"
              v-model="formData.function_name"
              type="text"
              required
              placeholder="e.g., check_file"
            />
          </div>

          <div class="form-group">
            <label>Function Arguments</label>
            <div class="function-args">
              <div
                v-for="(arg, index) in argRows"
                :key="index"
                class="arg-row"
              >
                <input
                  v-model="argRows[index].key"
                  type="text"
                  placeholder="Argument name"
                  class="arg-name"
                />
                <input
                  v-model="argRows[index].value"
                  type="text"
                  placeholder="Argument description"
                  class="arg-value"
                />
                <button
                  type="button"
                  @click="removeArg(index)"
                  class="btn btn-danger btn-sm"
                  title="Remove argument"
                >
                  -
                </button>
              </div>
              <button
                type="button"
                @click="addArg"
                class="btn btn-secondary btn-sm"
              >
                + Add Argument
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="description">Description *</label>
            <textarea
              id="description"
              v-model="formData.description"
              required
              rows="3"
              placeholder="Describe what this test function does..."
            ></textarea>
          </div>

          <div class="form-group">
            <label for="category">Category *</label>
            <div class="category-selector">
              <select
                id="category"
                v-model="formData.category"
                required
              >
                <option value="">Select a category</option>
                <option
                  v-for="(desc, cat) in categories"
                  :key="cat"
                  :value="cat"
                >
                  {{ cat }} - {{ desc }}
                </option>
                <option v-if="newCategory" :value="newCategory">
                  {{ newCategory }} (new)
                </option>
              </select>
              <div class="category-actions">
                <button
                  type="button"
                  @click="showNewCategoryInput = !showNewCategoryInput"
                  class="btn btn-secondary btn-sm"
                >
                  {{ showNewCategoryInput ? 'Cancel' : 'New Category' }}
                </button>
              </div>
            </div>
            
            <div v-if="showNewCategoryInput" class="new-category-input">
              <input
                v-model="newCategory"
                type="text"
                placeholder="Enter new category name"
                class="category-input"
                @keyup.enter="addNewCategory"
              />
              <input
                v-model="newCategoryDescription"
                type="text"
                placeholder="Category description"
                class="category-description"
                @keyup.enter="addNewCategory"
              />
              <button
                type="button"
                @click="addNewCategory"
                class="btn btn-primary btn-sm"
                :disabled="!newCategory.trim()"
              >
                Add
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Platform Support *</label>
            <div class="platform-checkboxes">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="formData.platform_support"
                  value="windows"
                />
                Windows
              </label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="formData.platform_support"
                  value="linux"
                />
                Linux
              </label>
            </div>
          </div>

          <div class="form-group">
            <label for="return_structure">Return Structure *</label>
            <div class="json-editor">
              <textarea
                id="return_structure"
                v-model="returnStructureJson"
                @input="validateJson"
                rows="6"
                placeholder='{
  "stdout": "str - Standard output message",
  "stderr": "str - Error output message",
  "exception": "str - Exception message if any",
  "returncode": "int - 0 for success, non-zero for failure"
}'
                :class="{ 'json-error': jsonError }"
              ></textarea>
              <div v-if="jsonError" class="error-message">
                Invalid JSON: {{ jsonError }}
              </div>
            </div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button @click="cancel" class="btn btn-secondary">Cancel</button>
        <button 
          @click="save" 
          class="btn btn-primary"
          :disabled="!isFormValid"
        >
          {{ isEditing ? 'Update' : 'Create' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'TestCatalogModal',
  props: {
    testFunction: {
      type: Object,
      default: () => ({})
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    categories: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const formData = ref({
      script_path: '',
      function_name: '',
      function_args: {},
      description: '',
      category: '',
      platform_support: [],
      return_structure: {}
    })

    const argRows = ref([])
    const returnStructureJson = ref('')
    const jsonError = ref('')
    const showNewCategoryInput = ref(false)
    const newCategory = ref('')
    const newCategoryDescription = ref('')

    // Initialize form data when props change
    watch(() => props.testFunction, (newTestFunction) => {
      if (newTestFunction) {
        formData.value = { ...newTestFunction }
        
        // Convert function_args object to array of objects for editing
        const args = formData.value.function_args || {}
        argRows.value = Object.entries(args).map(([key, value]) => ({
          key,
          value
        }))
        
        // Convert return_structure to JSON string
        try {
          returnStructureJson.value = JSON.stringify(formData.value.return_structure, null, 2)
        } catch {
          returnStructureJson.value = '{}'
        }
      } else {
        // Initialize with empty array for new function
        argRows.value = []
      }
    }, { immediate: true })

    const addArg = () => {
      argRows.value.push({ key: '', value: '' })
    }

    const removeArg = (index) => {
      argRows.value.splice(index, 1)
    }

    const addNewCategory = () => {
      if (newCategory.value.trim()) {
        // Add the new category to the categories object
        props.categories[newCategory.value.trim()] = newCategoryDescription.value.trim() || 'New category'
        
        // Select the new category
        formData.value.category = newCategory.value.trim()
        
        // Reset the new category inputs
        newCategory.value = ''
        newCategoryDescription.value = ''
        showNewCategoryInput.value = false
      }
    }

    const validateJson = () => {
      try {
        if (returnStructureJson.value.trim()) {
          JSON.parse(returnStructureJson.value)
        }
        jsonError.value = ''
      } catch (error) {
        jsonError.value = error.message
      }
    }

    const buildFunctionArgs = () => {
      const args = {}
      argRows.value.forEach(arg => {
        if (arg.key.trim() && arg.value.trim()) {
          args[arg.key.trim()] = arg.value.trim()
        }
      })
      return args
    }

    const buildReturnStructure = () => {
      try {
        return returnStructureJson.value.trim() ? JSON.parse(returnStructureJson.value) : {}
      } catch {
        return {}
      }
    }

    const isFormValid = computed(() => {
      return (
        formData.value.script_path.trim() &&
        formData.value.function_name.trim() &&
        formData.value.description.trim() &&
        formData.value.category.trim() &&
        formData.value.platform_support.length > 0 &&
        !jsonError.value
      )
    })

    const save = () => {
      if (!isFormValid.value) return

      const functionArgs = buildFunctionArgs()
      const returnStructure = buildReturnStructure()

      const testFunctionData = {
        script_path: formData.value.script_path.trim(),
        function_name: formData.value.function_name.trim(),
        function_args: functionArgs,
        description: formData.value.description.trim(),
        category: formData.value.category,
        platform_support: formData.value.platform_support,
        return_structure: returnStructure
      }

      emit('save', testFunctionData)
    }

    const cancel = () => {
      emit('cancel')
    }

    const handleOverlayClick = (event) => {
      if (event.target.classList.contains('modal-overlay')) {
        cancel()
      }
    }

    return {
      formData,
      argRows,
      returnStructureJson,
      jsonError,
      showNewCategoryInput,
      newCategory,
      newCategoryDescription,
      addArg,
      removeArg,
      addNewCategory,
      validateJson,
      isFormValid,
      save,
      cancel,
      handleOverlayClick
    }
  }
}
</script>

<style scoped>
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
  max-width: 600px;
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
  color: #e74c3c;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
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

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.function-args {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
}

.arg-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.arg-name {
  flex: 1;
}

.arg-value {
  flex: 2;
}

.category-selector {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.category-selector select {
  flex: 1;
}

.category-actions {
  flex-shrink: 0;
}

.new-category-input {
  margin-top: 0.5rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.category-input {
  flex: 1;
}

.category-description {
  flex: 2;
}

.platform-checkboxes {
  display: flex;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.json-editor textarea {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.json-editor textarea.json-error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.25rem;
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
</style>
