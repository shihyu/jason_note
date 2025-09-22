/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import * as Messages from './Messages';
export declare function getMessageClassFromMessage(msg: Messages.ButtplugMessage): (new (...args: unknown[]) => Messages.ButtplugMessage) | null;
export declare function fromJSON(str: any): Messages.ButtplugMessage[];
