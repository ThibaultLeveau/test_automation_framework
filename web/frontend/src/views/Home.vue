<template>
  <div class="home">
    <div class="hero-section">
      <h2>Welcome to Test Automation Framework</h2>
      <p class="subtitle">Manage your test plans, catalog, execution logs, and variables through a modern web interface</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card">
        <h3>Test Plans</h3>
        <p>Create, edit, and manage your test plans with visual interface</p>
        <div class="card-stats">
          <span class="stat-value">{{ testPlansCount }}</span>
          <span class="stat-label">Available Plans</span>
        </div>
        <router-link to="/test-plans" class="card-action">Manage Test Plans</router-link>
      </div>

      <div class="dashboard-card">
        <h3>Test Catalog</h3>
        <p>Browse available test functions and their documentation</p>
        <div class="card-stats">
          <span class="stat-value">{{ testFunctionsCount }}</span>
          <span class="stat-label">Test Functions</span>
        </div>
        <router-link to="/test-catalog" class="card-action">Browse Catalog</router-link>
      </div>

      <div class="dashboard-card">
        <h3>Execution Logs</h3>
        <p>Monitor test executions and view detailed logs</p>
        <div class="card-stats">
          <span class="stat-value">{{ executionLogsCount }}</span>
          <span class="stat-label">Recent Executions</span>
        </div>
        <router-link to="/execution" class="card-action">View Logs</router-link>
      </div>

      <div class="dashboard-card">
        <h3>Variables</h3>
        <p>Manage global and test-specific variables</p>
        <div class="card-stats">
          <span class="stat-value">{{ variablesCount }}</span>
          <span class="stat-label">Variables</span>
        </div>
        <router-link to="/variables" class="card-action">Manage Variables</router-link>
      </div>
    </div>

    <div class="system-status">
      <h3>System Status</h3>
      <div class="status-grid">
        <div class="status-item" :class="{ 'status-ok': apiStatus === 'running', 'status-error': apiStatus !== 'running' }">
          <span class="status-indicator"></span>
          <span class="status-label">API Server</span>
          <span class="status-value">{{ apiStatus }}</span>
        </div>
        <div class="status-item status-ok">
          <span class="status-indicator"></span>
          <span class="status-label">Frontend</span>
          <span class="status-value">running</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Home',
  setup() {
    const testPlansCount = ref(0)
    const testFunctionsCount = ref(0)
    const executionLogsCount = ref(0)
    const variablesCount = ref(0)
    const apiStatus = ref('checking...')

    const fetchDashboardData = async () => {
      try {
        // Check API status
        const statusResponse = await axios.get('/api')
        apiStatus.value = statusResponse.data.status

        // Fetch test plans count
        const plansResponse = await axios.get('/api/test-plans')
        testPlansCount.value = plansResponse.data.length

        // Fetch test catalog
        const catalogResponse = await axios.get('/api/test-catalog')
        testFunctionsCount.value = catalogResponse.data.scripts?.length || 0

        // Fetch variables count
        const variablesResponse = await axios.get('/api/variables')
        variablesCount.value = Object.keys(variablesResponse.data).length

        // For now, set execution logs to 0 (will be implemented later)
        executionLogsCount.value = 0

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        apiStatus.value = 'error'
      }
    }

    onMounted(() => {
      fetchDashboardData()
    })

    return {
      testPlansCount,
      testFunctionsCount,
      executionLogsCount,
      variablesCount,
      apiStatus
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 100%;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem 0;
}

.hero-section h2 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.dashboard-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.dashboard-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.dashboard-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.card-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #3498db;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.card-action {
  display: block;
  text-align: center;
  background: #3498db;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.3s;
}

.card-action:hover {
  background: #2980b9;
}

.system-status {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.system-status h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 6px;
  background: #f8f9fa;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #95a5a6;
}

.status-ok .status-indicator {
  background: #27ae60;
}

.status-error .status-indicator {
  background: #e74c3c;
}

.status-label {
  flex: 1;
  font-weight: 500;
  color: #2c3e50;
}

.status-value {
  color: #7f8c8d;
  font-weight: 500;
}
</style>
