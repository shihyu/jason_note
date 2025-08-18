/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
exports.ButtplugNodeWebsocketClientConnector = void 0;
const ButtplugBrowserWebsocketClientConnector_1 = require("./ButtplugBrowserWebsocketClientConnector");
const ws_1 = require("ws");
class ButtplugNodeWebsocketClientConnector extends ButtplugBrowserWebsocketClientConnector_1.ButtplugBrowserWebsocketClientConnector {
    constructor() {
        super(...arguments);
        this._websocketConstructor = ws_1.WebSocket;
    }
}
exports.ButtplugNodeWebsocketClientConnector = ButtplugNodeWebsocketClientConnector;
//# sourceMappingURL=ButtplugNodeWebsocketClientConnector.js.map