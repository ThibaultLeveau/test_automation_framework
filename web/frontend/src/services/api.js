// API service for backend communication
const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Test Plans endpoints
  async getTestPlans() {
    return this.request('/test-plans');
  }

  async getTestPlan(id) {
    return this.request(`/test-plans/${id}`);
  }

  async createTestPlan(testPlan) {
    return this.request('/test-plans', {
      method: 'POST',
      body: JSON.stringify(testPlan),
    });
  }

  async updateTestPlan(id, testPlan) {
    return this.request(`/test-plans/${id}`, {
      method: 'PUT',
      body: JSON.stringify(testPlan),
    });
  }

  async deleteTestPlan(id) {
    return this.request(`/test-plans/${id}`, {
      method: 'DELETE',
    });
  }

  // Test Catalog endpoints
  async getTestCatalog() {
    return this.request('/test-catalog');
  }

  async createTestFunction(testFunction) {
    return this.request('/test-catalog', {
      method: 'POST',
      body: JSON.stringify(testFunction),
    });
  }

  async updateTestFunction(functionIndex, testFunction) {
    return this.request(`/test-catalog/${functionIndex}`, {
      method: 'PUT',
      body: JSON.stringify(testFunction),
    });
  }

  async deleteTestFunction(functionIndex) {
    return this.request(`/test-catalog/${functionIndex}`, {
      method: 'DELETE',
    });
  }

  // Variables endpoints
  async getVariables() {
    return this.request('/variables');
  }

  async createVariable(variable) {
    return this.request('/variables', {
      method: 'POST',
      body: JSON.stringify(variable),
    });
  }

  async updateVariable(variableName, variable) {
    return this.request(`/variables/${variableName}`, {
      method: 'PUT',
      body: JSON.stringify(variable),
    });
  }

  async deleteVariable(variableName) {
    return this.request(`/variables/${variableName}`, {
      method: 'DELETE',
    });
  }

  // Execution Log endpoints
  async getExecutionLogs() {
    return this.request('/execution-log');
  }

  async getExecutionLog(filename) {
    return this.request(`/execution-log/${filename}`);
  }

  async deleteExecutionLog(filename) {
    return this.request(`/execution-log/${filename}`, {
      method: 'DELETE',
    });
  }

  async deleteExecutionLogs(filenames) {
    return this.request('/execution-log/bulk-delete', {
      method: 'POST',
      body: JSON.stringify(filenames),
    });
  }
}

export default new ApiService();
