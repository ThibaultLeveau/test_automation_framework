### Code architecture

web/
  backend/                    
    main.py         # FastAPI backend : contains api endpoints, middleware ...
  frontend/                  
    src/
      Views/        # VueJS frontend : Contains the web views like Home, testplans, variables ...
      App.vue       # base view
      main.js
    index.html
    vite.config.js

### Backend API

/api/test-plans - Return combinaison of all .json test plans in /test_plans
/api/variables - Return variables.json in /configs
/api/test-catalog - Return script_catalog.json in /script
/api/execution-log - Return combinaison of all .json test plans in /test_execution_log
/api/test-execution - Request execution