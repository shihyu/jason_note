// Environment shim for WASM module - instant crate support
export const now = function() {
  return performance.now();
};

// Alternative timing functions
export const time = function() {
  return Date.now();
};

export const clock_time_get = function(id, precision, time) {
  // WASI clock_time_get implementation
  const now_ms = Date.now();
  const now_ns = BigInt(now_ms) * 1000000n;
  // Write the time as little-endian 64-bit integer
  const view = new DataView(memory.buffer);
  view.setBigUint64(time, now_ns, true);
  return 0;
};

// Standard wasm-bindgen functions
export const __wbindgen_string_new = function() {};
export const __wbindgen_object_drop_ref = function() {};
export const __wbindgen_cb_drop = function() {};
export const __wbindgen_describe = function() {};
export const __wbindgen_closure_wrapper = function() {};
export const __wbindgen_string_get = function() {};
export const __wbindgen_number_get = function() {};
export const __wbindgen_boolean_get = function() {};
export const __wbindgen_is_null = function() {};
export const __wbindgen_is_undefined = function() {};
export const __wbg_log_46c9addd26de6e73 = function() {};
export const __wbg_warn_3cd0a3ceea5a5ac3 = function() {};
export const __wbg_error_bb3b6bddedbb6a86 = function() {};
export const __wbindgen_throw = function() {};