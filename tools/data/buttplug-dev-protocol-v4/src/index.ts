import { ButtplugMessage, IButtplugClientConnector, fromJSON } from 'buttplug';
import { EventEmitter } from 'eventemitter3';

export class ButtplugWasmClientConnector extends EventEmitter implements IButtplugClientConnector {
  private static _loggingActivated = false;
  private static wasmInstance: any;
  private _connected: boolean = false;
  private client: any;
  private serverPtr: any;

  constructor() {
    super();
  }
  
  public get Connected(): boolean { return this._connected }

  private static maybeLoadWasm = async() => {
    if (ButtplugWasmClientConnector.wasmInstance == undefined) {
      try {
        // 嘗試從生成的 pkg 目錄加載 WASM 模組
        const wasmModule = await import('../crates/buttplug_server/pkg/buttplug_server.js');
        // 對於 web 目標，需要手動初始化 WASM
        // 使用公共路徑中的 WASM 檔案
        await wasmModule.default('./wasm/buttplug_server_bg.wasm');
        ButtplugWasmClientConnector.wasmInstance = wasmModule;
      } catch (error) {
        console.error('Failed to load WASM module:', error);
        throw error;
      }
    }    
  }
  
  public static activateLogging = async (logLevel: string = "debug") => {
    await ButtplugWasmClientConnector.maybeLoadWasm();
    if (this._loggingActivated) {
      console.log("Logging already activated, ignoring.");
      return;
    }
    console.log("Turning on logging.");
    ButtplugWasmClientConnector.wasmInstance.buttplug_activate_env_logger(logLevel);
  }

  public initialize = async (): Promise<void> => {};

  public connect = async (): Promise<void> => {
    await ButtplugWasmClientConnector.maybeLoadWasm();
    
    // Enable logging for debugging
    try {
      ButtplugWasmClientConnector.wasmInstance.buttplug_activate_env_logger('debug');
    } catch (e) {
      console.log("Logging activation failed:", e);
    }
    
    this.client = ButtplugWasmClientConnector.wasmInstance.buttplug_create_embedded_wasm_server((msgs) => {
      this.emitMessage(msgs);
    });
    
    if (!this.client || this.client === 0) {
      throw new Error("Failed to create WASM server - returned null pointer");
    }
    
    this._connected = true;
  };

  public disconnect = async (): Promise<void> => {};

  public send = (msg: ButtplugMessage): void => {
    ButtplugWasmClientConnector.wasmInstance.buttplug_client_send_json_message(this.client, new TextEncoder().encode('[' + msg.toJSON() + ']'), (output) => {
      this.emitMessage(output);
    });
  };

  private emitMessage = (msg: Uint8Array) => {
    let str = new TextDecoder().decode(msg);
    // This needs to use buttplug-js's fromJSON, otherwise we won't resolve the message name correctly.
    this.emit('message', fromJSON(str));
  }
}