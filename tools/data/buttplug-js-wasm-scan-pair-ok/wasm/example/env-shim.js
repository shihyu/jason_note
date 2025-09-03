// Environment shim for WASM
export const env = {
  memory: new WebAssembly.Memory({ initial: 256, maximum: 256 }),
};

// Export individual functions that might be needed
export const memory = env.memory;
export const __linear_memory = env.memory;
export const __indirect_function_table = new WebAssembly.Table({ initial: 0, element: 'anyfunc' });

// Time function - returns current time in milliseconds
export const now = () => {
  return Date.now();
};

// Console functions
export const console_log = (ptr, len) => {
  // Implementation would depend on how the WASM passes strings
  console.log('WASM log:', ptr, len);
};

export const console_error = (ptr, len) => {
  console.error('WASM error:', ptr, len);
};

// Abort function
export const abort = () => {
  throw new Error('WASM abort');
};

// Math functions that might be needed
export const random = Math.random;
export const floor = Math.floor;
export const ceil = Math.ceil;
export const round = Math.round;

// Default exports
export default env;