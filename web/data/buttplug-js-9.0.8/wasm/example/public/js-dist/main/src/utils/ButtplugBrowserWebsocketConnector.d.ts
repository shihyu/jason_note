/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import { EventEmitter } from 'eventemitter3';
import { ButtplugMessage } from '../core/Messages';
export declare class ButtplugBrowserWebsocketConnector extends EventEmitter {
    private _url;
    protected _ws: WebSocket | undefined;
    protected _websocketConstructor: typeof WebSocket | null;
    constructor(_url: string);
    get Connected(): boolean;
    connect: () => Promise<void>;
    disconnect: () => Promise<void>;
    sendMessage(msg: ButtplugMessage): void;
    initialize: () => Promise<void>;
    protected parseIncomingMessage(event: MessageEvent): void;
    protected onReaderLoad(event: Event): void;
}
