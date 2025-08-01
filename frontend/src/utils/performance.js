// Development utilities for performance monitoring
export const isDevelopment = process.env.NODE_ENV === 'development';

export const measurePerformance = (name, fn) => {
  if (!isDevelopment) return fn();
  
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  
  console.log(`⏱️ ${name}: ${(end - start).toFixed(2)}ms`);
  return result;
};

export const logRenderInfo = (componentName, props = {}) => {
  if (!isDevelopment) return;
  
  console.group(`🔄 ${componentName} rendered`);
  console.log('📝 Props:', props);
  console.log('⏰ Time:', new Date().toLocaleTimeString());
  console.groupEnd();
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
