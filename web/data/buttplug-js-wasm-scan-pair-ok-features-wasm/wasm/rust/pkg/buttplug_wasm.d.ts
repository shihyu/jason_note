/* tslint:disable */
/* eslint-disable */
/**
* @param {Function} callback
* @returns {number}
*/
export function buttplug_create_embedded_wasm_server(callback: Function): number;
/**
* @param {number} ptr
*/
export function buttplug_free_embedded_wasm_server(ptr: number): void;
/**
* @param {number} server_ptr
* @param {Uint8Array} buf
* @param {Function} callback
*/
export function buttplug_client_send_json_message(server_ptr: number, buf: Uint8Array, callback: Function): void;
/**
* @param {string} max_level
*/
export function buttplug_activate_env_logger(max_level: string): void;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly buttplug_create_embedded_wasm_server: (a: number) => number;
  readonly buttplug_free_embedded_wasm_server: (a: number) => void;
  readonly buttplug_client_send_json_message: (a: number, b: number, c: number, d: number) => void;
  readonly buttplug_activate_env_logger: (a: number, b: number) => void;
  readonly __wbindgen_malloc: (a: number, b: number) => number;
  readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
  readonly __wbindgen_export_2: WebAssembly.Table;
  readonly _dyn_core__ops__function__FnMut__A____Output___R_as_wasm_bindgen__closure__WasmClosure___describe__invoke__h33a01e7a38cda320: (a: number, b: number, c: number) => void;
  readonly _dyn_core__ops__function__FnMut__A____Output___R_as_wasm_bindgen__closure__WasmClosure___describe__invoke__hc44787be12a84c39: (a: number, b: number, c: number) => void;
  readonly _dyn_core__ops__function__FnMut_____Output___R_as_wasm_bindgen__closure__WasmClosure___describe__invoke__h5c1a3eb48a5b7bb9: (a: number, b: number) => void;
  readonly __wbindgen_free: (a: number, b: number, c: number) => void;
  readonly __wbindgen_exn_store: (a: number) => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;
/**
* Instantiates the given `module`, which can either be bytes or
* a precompiled `WebAssembly.Module`.
*
* @param {SyncInitInput} module
*
* @returns {InitOutput}
*/
export function initSync(module: SyncInitInput): InitOutput;

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {InitInput | Promise<InitInput>} module_or_path
*
* @returns {Promise<InitOutput>}
*/
export default function __wbg_init (module_or_path?: InitInput | Promise<InitInput>): Promise<InitOutput>;
