import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Home from './views/Home.vue'
import TestPlans from './views/TestPlans.vue'
import TestPlanDetail from './views/TestPlanDetail.vue'
import TestCatalog from './views/TestCatalog.vue'
import Variables from './views/Variables.vue'
import ExecutionLogs from './views/ExecutionLogs.vue'
import ExecutionLogDetail from './views/ExecutionLogDetail.vue'
import TestExecution from './views/TestExecution.vue'

// Create router
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/test-plans',
      name: 'TestPlans',
      component: TestPlans
    },
    {
      path: '/test-plans/:id',
      name: 'TestPlanDetail',
      component: TestPlanDetail
    },
    {
      path: '/test-catalog',
      name: 'TestCatalog',
      component: TestCatalog
    },
    {
      path: '/variables',
      name: 'Variables',
      component: Variables
    },
    {
      path: '/execution-logs',
      name: 'ExecutionLogs',
      component: ExecutionLogs
    },
    {
      path: '/execution-logs/:filename',
      name: 'ExecutionLogDetail',
      component: ExecutionLogDetail
    },
    {
      path: '/test-execution',
      name: 'TestExecution',
      component: TestExecution
    }
  ]
})

// Create Pinia store
const pinia = createPinia()

// Create and mount the app
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')
