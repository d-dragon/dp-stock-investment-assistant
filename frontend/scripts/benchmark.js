const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Performance testing script
class ReactStartupBenchmark {
  constructor() {
    this.results = [];
    this.iterations = 3;
  }

  async runBenchmark() {
    console.log('🚀 Starting React Startup Performance Benchmark');
    console.log(`📊 Running ${this.iterations} iterations...`);

    for (let i = 1; i <= this.iterations; i++) {
      console.log(`\n🔄 Iteration ${i}/${this.iterations}`);
      const result = await this.measureStartup();
      this.results.push(result);
      
      // Wait between iterations
      if (i < this.iterations) {
        console.log('⏳ Waiting 5 seconds before next iteration...');
        await this.wait(5000);
      }
    }

    this.generateReport();
  }

  async measureStartup() {
    const startTime = Date.now();
    
    return new Promise((resolve) => {
      // Clear cache first
      this.clearCache();
      
      const process = exec('npm start', { cwd: __dirname });
      
      process.stdout.on('data', (data) => {
        const output = data.toString();
        
        // Look for webpack compilation complete
        if (output.includes('webpack compiled') || output.includes('Compiled successfully')) {
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          console.log(`✅ Startup completed in ${duration}ms`);
          
          // Kill the process
          process.kill();
          
          resolve({
            duration,
            timestamp: new Date().toISOString(),
            success: true
          });
        }
      });

      process.stderr.on('data', (data) => {
        console.error('❌ Error:', data.toString());
      });

      // Timeout after 60 seconds
      setTimeout(() => {
        process.kill();
        resolve({
          duration: 60000,
          timestamp: new Date().toISOString(),
          success: false,
          error: 'Timeout'
        });
      }, 60000);
    });
  }

  clearCache() {
    const cachePaths = [
      'node_modules/.cache',
      '.cache',
      'build'
    ];

    cachePaths.forEach(cachePath => {
      if (fs.existsSync(cachePath)) {
        console.log(`🧹 Clearing cache: ${cachePath}`);
        fs.rmSync(cachePath, { recursive: true, force: true });
      }
    });
  }

  generateReport() {
    console.log('\n📊 PERFORMANCE REPORT');
    console.log('====================');

    const successfulRuns = this.results.filter(r => r.success);
    
    if (successfulRuns.length === 0) {
      console.log('❌ No successful runs recorded');
      return;
    }

    const durations = successfulRuns.map(r => r.duration);
    const average = durations.reduce((a, b) => a + b, 0) / durations.length;
    const min = Math.min(...durations);
    const max = Math.max(...durations);

    console.log(`📈 Average startup time: ${average.toFixed(0)}ms`);
    console.log(`⚡ Fastest startup: ${min}ms`);
    console.log(`🐌 Slowest startup: ${max}ms`);
    console.log(`✅ Success rate: ${successfulRuns.length}/${this.results.length}`);

    // Performance recommendations
    this.generateRecommendations(average);
  }

  generateRecommendations(averageTime) {
    console.log('\n💡 OPTIMIZATION RECOMMENDATIONS');
    console.log('===============================');

    if (averageTime > 10000) {
      console.log('🔴 SLOW: Consider these optimizations:');
      console.log('   • Use npm ci instead of npm install');
      console.log('   • Enable persistent caching');
      console.log('   • Reduce bundle size');
      console.log('   • Use faster disk (SSD)');
    } else if (averageTime > 5000) {
      console.log('🟡 MODERATE: Minor optimizations possible:');
      console.log('   • Enable webpack caching');
      console.log('   • Optimize imports');
    } else {
      console.log('🟢 GOOD: Startup time is optimal!');
    }
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Run benchmark if called directly
if (require.main === module) {
  const benchmark = new ReactStartupBenchmark();
  benchmark.runBenchmark().catch(console.error);
}

module.exports = ReactStartupBenchmark;
