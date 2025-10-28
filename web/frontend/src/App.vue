<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <h1>Test Automation Framework</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/test-plans" class="nav-link">Test Plans</router-link>
          <router-link to="/test-catalog" class="nav-link">Test Catalog</router-link>
          <router-link to="/execution" class="nav-link">Execution</router-link>
          <router-link to="/variables" class="nav-link">Variables</router-link>
        </nav>
      </div>
    </header>
    
    <main class="main-content">
      <div class="container">
        <router-view />
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 Test Automation Framework - Web Interface</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.nav {
  margin-top: 1rem;
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #ecf0f1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background-color: #34495e;
  color: white;
}

.main-content {
  min-height: calc(100vh - 140px);
  padding: 2rem 0;
}

.app-footer {
  background-color: #34495e;
  color: #ecf0f1;
  text-align: center;
  padding: 1rem 0;
  margin-top: auto;
}

.app-footer p {
  margin: 0;
}
</style>
