/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
exports.ButtplugBrowserWebsocketClientConnector = void 0;
const ButtplugBrowserWebsocketConnector_1 = require("../utils/ButtplugBrowserWebsocketConnector");
class ButtplugBrowserWebsocketClientConnector extends ButtplugBrowserWebsocketConnector_1.ButtplugBrowserWebsocketConnector {
    constructor() {
        super(...arguments);
        this.send = (msg) => {
            if (!this.Connected) {
                throw new Error('ButtplugClient not connected');
            }
            this.sendMessage(msg);
        };
    }
}
exports.ButtplugBrowserWebsocketClientConnector = ButtplugBrowserWebsocketClientConnector;
//# sourceMappingURL=ButtplugBrowserWebsocketClientConnector.js.map