<template>
  <div class="test-catalog">
    <div class="page-header">
      <h1>Test Catalog</h1>
      <button @click="createNewTestFunction" class="btn btn-primary">
        New Test Function
      </button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">Loading test catalog...</div>
      
      <div v-else-if="error" class="error">
        <p>Error loading test catalog: {{ error }}</p>
        <button @click="loadTestCatalog" class="btn btn-secondary">Retry</button>
      </div>

      <div v-else-if="testFunctions.length === 0" class="empty-state">
        <p>No test functions found.</p>
        <button @click="createNewTestFunction" class="btn btn-primary">
          Create Your First Test Function
        </button>
      </div>

      <div v-else class="test-catalog-table">
        <table class="data-table">
          <thead>
            <tr>
              <th>Function Name</th>
              <th>Script Path</th>
              <th>Description</th>
              <th>Category</th>
              <th>Platform Support</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(testFunction, index) in testFunctions" :key="index">
              <td class="function-name">{{ testFunction.function_name }}</td>
              <td>{{ testFunction.script_path }}</td>
              <td class="description">{{ testFunction.description }}</td>
              <td>
                <span class="category-tag">{{ testFunction.category }}</span>
              </td>
              <td>
                <div class="platform-tags">
                  <span 
                    v-for="platform in testFunction.platform_support" 
                    :key="platform"
                    :class="['platform-tag', platform]"
                  >
                    {{ platform }}
                  </span>
                </div>
              </td>
              <td>
                <button 
                  @click="editTestFunction(index)"
                  class="btn btn-secondary btn-sm"
                  title="Edit test function"
                >
                  Edit
                </button>
                <button 
                  @click="deleteTestFunction(index, testFunction.function_name)"
                  class="btn btn-danger btn-sm"
                  title="Delete test function"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Test Function Modal -->
    <TestCatalogModal
      v-if="showModal"
      :testFunction="editingFunction"
      :isEditing="isEditing"
      :categories="categories"
      @save="handleSaveTestFunction"
      @cancel="closeModal"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/api.js'
import TestCatalogModal from '../components/TestCatalogModal.vue'

export default {
  name: 'TestCatalog',
  components: {
    TestCatalogModal
  },
  setup() {
    const testCatalog = ref({})
    const testFunctions = ref([])
    const categories = ref({})
    const loading = ref(false)
    const error = ref(null)
    const showModal = ref(false)
    const editingFunction = ref(null)
    const isEditing = ref(false)

    const loadTestCatalog = async () => {
      loading.value = true
      error.value = null
      try {
        testCatalog.value = await apiService.getTestCatalog()
        testFunctions.value = testCatalog.value.scripts || []
        categories.value = testCatalog.value.categories || {}
      } catch (err) {
        error.value = err.message
        console.error('Failed to load test catalog:', err)
      } finally {
        loading.value = false
      }
    }

    const createNewTestFunction = () => {
      editingFunction.value = {
        script_path: '',
        function_name: '',
        function_args: {},
        description: '',
        category: '',
        platform_support: [],
        return_structure: {}
      }
      isEditing.value = false
      showModal.value = true
    }

    const editTestFunction = (index) => {
      editingFunction.value = { ...testFunctions.value[index] }
      isEditing.value = true
      showModal.value = true
    }

    const deleteTestFunction = async (index, functionName) => {
      if (!confirm(`Are you sure you want to delete the test function "${functionName}"?`)) {
        return
      }

      try {
        await apiService.deleteTestFunction(index)
        await loadTestCatalog() // Reload the list
      } catch (err) {
        alert(`Failed to delete test function: ${err.message}`)
      }
    }

    const handleSaveTestFunction = async (testFunctionData) => {
      try {
        if (isEditing.value) {
          // Find the index of the function being edited
          const index = testFunctions.value.findIndex(
            func => func.function_name === editingFunction.value.function_name
          )
          if (index !== -1) {
            await apiService.updateTestFunction(index, testFunctionData)
          }
        } else {
          await apiService.createTestFunction(testFunctionData)
        }
        
        await loadTestCatalog() // Reload the list
        closeModal()
      } catch (err) {
        alert(`Failed to save test function: ${err.message}`)
      }
    }

    const closeModal = () => {
      showModal.value = false
      editingFunction.value = null
      isEditing.value = false
    }

    onMounted(() => {
      loadTestCatalog()
    })

    return {
      testFunctions,
      categories,
      loading,
      error,
      showModal,
      editingFunction,
      isEditing,
      loadTestCatalog,
      createNewTestFunction,
      editTestFunction,
      deleteTestFunction,
      handleSaveTestFunction,
      closeModal
    }
  }
}
</script>

<style scoped>
.test-catalog {
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

.function-name {
  font-weight: 600;
  color: #2c3e50;
}

.description {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-tag {
  background-color: #e8f4fd;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.platform-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.platform-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.platform-tag.windows {
  background-color: #e8f6f3;
  color: #27ae60;
}

.platform-tag.linux {
  background-color: #fef9e7;
  color: #f39c12;
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
</style>
