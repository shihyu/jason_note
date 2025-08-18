import { defineConfig } from 'vite';
import { resolve } from 'path';
import wasm from 'vite-plugin-wasm';
import topLevelAwait from 'vite-plugin-top-level-await';

export default defineConfig({
  plugins: [
    wasm(),
    topLevelAwait()
  ],
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    exclude: ['env']
  },
  resolve: {
    alias: {
      '@buttplug': resolve(__dirname, '../../js/dist/web/buttplug.mjs'),
      '@wasm': resolve(__dirname, '../dist/buttplug-wasm.mjs'),
      'env': resolve(__dirname, './env-shim.js'),
    },
  },
});