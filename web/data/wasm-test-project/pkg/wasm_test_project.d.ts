/* tslint:disable */
/* eslint-disable */
export function main(): void;
export function test_basic_math(a: number, b: number): number;
export function test_string_processing(input: string): string;
export function test_heavy_computation(n: number): number;
export function test_array_processing(data: Int32Array): Int32Array;
export function test_error_handling(should_fail: boolean): string;
export function test_performance_benchmark(): number;
export function get_memory_info(): string;
export function debug_trace(message: string): void;
export function run_all_tests(): string;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly main: () => void;
  readonly test_basic_math: (a: number, b: number) => number;
  readonly test_string_processing: (a: number, b: number) => [number, number];
  readonly test_heavy_computation: (a: number) => number;
  readonly test_array_processing: (a: number, b: number) => [number, number];
  readonly test_error_handling: (a: number) => [number, number, number, number];
  readonly test_performance_benchmark: () => number;
  readonly get_memory_info: () => [number, number];
  readonly debug_trace: (a: number, b: number) => void;
  readonly run_all_tests: () => [number, number];
  readonly __wbindgen_export_0: WebAssembly.Table;
  readonly __wbindgen_malloc: (a: number, b: number) => number;
  readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
  readonly __wbindgen_free: (a: number, b: number, c: number) => void;
  readonly __externref_table_dealloc: (a: number) => void;
  readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;
/**
* Instantiates the given `module`, which can either be bytes or
* a precompiled `WebAssembly.Module`.
*
* @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
*
* @returns {InitOutput}
*/
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
*
* @returns {Promise<InitOutput>}
*/
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
