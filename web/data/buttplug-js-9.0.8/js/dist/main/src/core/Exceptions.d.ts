/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import * as Messages from './Messages';
import { ButtplugLogger } from './Logging';
export declare class ButtplugError extends Error {
    get ErrorClass(): Messages.ErrorClass;
    get InnerError(): Error | undefined;
    get Id(): number | undefined;
    get ErrorMessage(): Messages.ButtplugMessage;
    static LogAndError<T extends ButtplugError>(constructor: new (str: string, num: number) => T, logger: ButtplugLogger, message: string, id?: number): T;
    static FromError(error: Messages.Error): ButtplugDeviceError | ButtplugInitError | ButtplugUnknownError | ButtplugPingError | ButtplugMessageError;
    errorClass: Messages.ErrorClass;
    innerError: Error | undefined;
    messageId: number | undefined;
    protected constructor(message: string, errorClass: Messages.ErrorClass, id?: number, inner?: Error);
}
export declare class ButtplugInitError extends ButtplugError {
    constructor(message: string, id?: number);
}
export declare class ButtplugDeviceError extends ButtplugError {
    constructor(message: string, id?: number);
}
export declare class ButtplugMessageError extends ButtplugError {
    constructor(message: string, id?: number);
}
export declare class ButtplugPingError extends ButtplugError {
    constructor(message: string, id?: number);
}
export declare class ButtplugUnknownError extends ButtplugError {
    constructor(message: string, id?: number);
}
