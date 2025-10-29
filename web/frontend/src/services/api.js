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

  // Other endpoints
  async getVariables() {
    return this.request('/variables');
  }
}

export default new ApiService();
