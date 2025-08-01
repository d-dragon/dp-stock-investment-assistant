#!/usr/bin/env node

// Performance monitoring script
const fs = require('fs');
const path = require('path');

const logPerformance = () => {
  const start = Date.now();
  
  console.log('🚀 Starting React development server...');
  console.log(`⏰ Start time: ${new Date().toLocaleTimeString()}`);
  
  // Monitor startup time
  const originalConsoleLog = console.log;
  console.log = (...args) => {
    if (args[0] && args[0].includes('webpack compiled')) {
      const duration = Date.now() - start;
      originalConsoleLog(`✅ Compilation complete in ${duration}ms`);
      originalConsoleLog(`🌐 Server ready at: http://localhost:3000`);
    }
    originalConsoleLog(...args);
  };
};

if (require.main === module) {
  logPerformance();
}

module.exports = { logPerformance };
