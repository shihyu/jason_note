import * as wasm from "./buttplug_server_bg.wasm";
export * from "./buttplug_server_bg.js";
import { __wbg_set_wasm } from "./buttplug_server_bg.js";
__wbg_set_wasm(wasm);
wasm.__wbindgen_start();
