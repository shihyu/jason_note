/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
'use strict';
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ButtplugBrowserWebsocketConnector = void 0;
const eventemitter3_1 = require("eventemitter3");
const MessageUtils_1 = require("../core/MessageUtils");
class ButtplugBrowserWebsocketConnector extends eventemitter3_1.EventEmitter {
    constructor(_url) {
        super();
        this._url = _url;
        this._websocketConstructor = null;
        this.connect = () => __awaiter(this, void 0, void 0, function* () {
            return new Promise((resolve, reject) => {
                var _a;
                const ws = new ((_a = this._websocketConstructor) !== null && _a !== void 0 ? _a : WebSocket)(this._url);
                const onErrorCallback = (event) => { reject(event); };
                const onCloseCallback = (event) => reject(event.reason);
                ws.addEventListener('open', () => __awaiter(this, void 0, void 0, function* () {
                    this._ws = ws;
                    try {
                        yield this.initialize();
                        this._ws.addEventListener('message', (msg) => {
                            this.parseIncomingMessage(msg);
                        });
                        this._ws.removeEventListener('close', onCloseCallback);
                        this._ws.removeEventListener('error', onErrorCallback);
                        this._ws.addEventListener('close', this.disconnect);
                        resolve();
                    }
                    catch (e) {
                        reject(e);
                    }
                }));
                // In websockets, our error rarely tells us much, as for security reasons
                // browsers usually only throw Error Code 1006. It's up to those using this
                // library to state what the problem might be.
                ws.addEventListener('error', onErrorCallback);
                ws.addEventListener('close', onCloseCallback);
            });
        });
        this.disconnect = () => __awaiter(this, void 0, void 0, function* () {
            if (!this.Connected) {
                return;
            }
            this._ws.close();
            this._ws = undefined;
            this.emit('disconnect');
        });
        this.initialize = () => __awaiter(this, void 0, void 0, function* () {
            return Promise.resolve();
        });
    }
    get Connected() {
        return this._ws !== undefined;
    }
    sendMessage(msg) {
        if (!this.Connected) {
            throw new Error('ButtplugBrowserWebsocketConnector not connected');
        }
        this._ws.send('[' + msg.toJSON() + ']');
    }
    parseIncomingMessage(event) {
        if (typeof event.data === 'string') {
            const msgs = (0, MessageUtils_1.fromJSON)(event.data);
            this.emit('message', msgs);
        }
        else if (event.data instanceof Blob) {
            // No-op, we only use text message types.
        }
    }
    onReaderLoad(event) {
        const msgs = (0, MessageUtils_1.fromJSON)(event.target.result);
        this.emit('message', msgs);
    }
}
exports.ButtplugBrowserWebsocketConnector = ButtplugBrowserWebsocketConnector;
//# sourceMappingURL=ButtplugBrowserWebsocketConnector.js.map