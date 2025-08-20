/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import { ButtplugLogger } from '../core/Logging';
import { EventEmitter } from 'eventemitter3';
import { ButtplugClientDevice } from './ButtplugClientDevice';
import { IButtplugClientConnector } from './IButtplugClientConnector';
import * as Messages from '../core/Messages';
export declare class ButtplugClient extends EventEmitter {
    protected _pingTimer: NodeJS.Timeout | null;
    protected _connector: IButtplugClientConnector | null;
    protected _devices: Map<number, ButtplugClientDevice>;
    protected _clientName: string;
    protected _logger: ButtplugLogger;
    protected _isScanning: boolean;
    private _sorter;
    constructor(clientName?: string);
    get connected(): boolean;
    get devices(): ButtplugClientDevice[];
    get isScanning(): boolean;
    connect: (connector: IButtplugClientConnector) => Promise<void>;
    disconnect: () => Promise<void>;
    startScanning: () => Promise<void>;
    stopScanning: () => Promise<void>;
    stopAllDevices: () => Promise<void>;
    private sendDeviceMessage;
    protected disconnectHandler: () => void;
    protected parseMessages: (msgs: Messages.ButtplugMessage[]) => void;
    protected initializeConnection: () => Promise<boolean>;
    protected requestDeviceList: () => Promise<void>;
    protected shutdownConnection: () => Promise<void>;
    protected sendMessage(msg: Messages.ButtplugMessage): Promise<Messages.ButtplugMessage>;
    protected checkConnector(): void;
    protected sendMsgExpectOk: (msg: Messages.ButtplugMessage) => Promise<void>;
    protected sendDeviceMessageClosure: (device: ButtplugClientDevice, msg: Messages.ButtplugDeviceMessage) => Promise<Messages.ButtplugMessage>;
}
