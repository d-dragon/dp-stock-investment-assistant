import React, { Profiler } from 'react';

// Performance profiler wrapper
const PerformanceProfiler = ({ children, id = 'app' }) => {
  const onRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
    if (process.env.NODE_ENV === 'development') {
      console.group(`🔍 Performance Profile: ${id}`);
      console.log(`📊 Phase: ${phase}`);
      console.log(`⏱️ Actual Duration: ${actualDuration.toFixed(2)}ms`);
      console.log(`🎯 Base Duration: ${baseDuration.toFixed(2)}ms`);
      console.log(`🚀 Start Time: ${startTime.toFixed(2)}ms`);
      console.log(`✅ Commit Time: ${commitTime.toFixed(2)}ms`);
      
      if (actualDuration > 16) {
        console.warn(`⚠️ Slow render detected! Consider optimization.`);
      }
      console.groupEnd();
    }
  };

  return (
    <Profiler id={id} onRender={onRenderCallback}>
      {children}
    </Profiler>
  );
};

export default PerformanceProfiler;
