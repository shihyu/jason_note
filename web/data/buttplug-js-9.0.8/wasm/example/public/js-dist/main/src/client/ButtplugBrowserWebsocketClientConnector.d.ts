/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import { IButtplugClientConnector } from './IButtplugClientConnector';
import { ButtplugMessage } from '../core/Messages';
import { ButtplugBrowserWebsocketConnector } from '../utils/ButtplugBrowserWebsocketConnector';
export declare class ButtplugBrowserWebsocketClientConnector extends ButtplugBrowserWebsocketConnector implements IButtplugClientConnector {
    send: (msg: ButtplugMessage) => void;
}
