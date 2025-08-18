/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import * as Messages from '../core/Messages';
export declare class ButtplugMessageSorter {
    private _useCounter;
    protected _counter: number;
    protected _waitingMsgs: Map<number, [
        (val: Messages.ButtplugMessage) => void,
        (err: Error) => void
    ]>;
    constructor(_useCounter: boolean);
    PrepareOutgoingMessage(msg: Messages.ButtplugMessage): Promise<Messages.ButtplugMessage>;
    ParseIncomingMessages(msgs: Messages.ButtplugMessage[]): Messages.ButtplugMessage[];
}
