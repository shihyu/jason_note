"use strict";
/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ButtplugUnknownError = exports.ButtplugPingError = exports.ButtplugMessageError = exports.ButtplugDeviceError = exports.ButtplugInitError = exports.ButtplugError = void 0;
const Messages = __importStar(require("./Messages"));
class ButtplugError extends Error {
    get ErrorClass() {
        return this.errorClass;
    }
    get InnerError() {
        return this.innerError;
    }
    get Id() {
        return this.messageId;
    }
    get ErrorMessage() {
        return new Messages.Error(this.message, this.ErrorClass, this.Id);
    }
    static LogAndError(constructor, logger, message, id = Messages.SYSTEM_MESSAGE_ID) {
        logger.Error(message);
        return new constructor(message, id);
    }
    static FromError(error) {
        switch (error.ErrorCode) {
            case Messages.ErrorClass.ERROR_DEVICE:
                return new ButtplugDeviceError(error.ErrorMessage, error.Id);
            case Messages.ErrorClass.ERROR_INIT:
                return new ButtplugInitError(error.ErrorMessage, error.Id);
            case Messages.ErrorClass.ERROR_UNKNOWN:
                return new ButtplugUnknownError(error.ErrorMessage, error.Id);
            case Messages.ErrorClass.ERROR_PING:
                return new ButtplugPingError(error.ErrorMessage, error.Id);
            case Messages.ErrorClass.ERROR_MSG:
                return new ButtplugMessageError(error.ErrorMessage, error.Id);
            default:
                throw new Error(`Message type ${error.ErrorCode} not handled`);
        }
    }
    constructor(message, errorClass, id = Messages.SYSTEM_MESSAGE_ID, inner) {
        super(message);
        this.errorClass = Messages.ErrorClass.ERROR_UNKNOWN;
        this.errorClass = errorClass;
        this.innerError = inner;
        this.messageId = id;
    }
}
exports.ButtplugError = ButtplugError;
class ButtplugInitError extends ButtplugError {
    constructor(message, id = Messages.SYSTEM_MESSAGE_ID) {
        super(message, Messages.ErrorClass.ERROR_INIT, id);
    }
}
exports.ButtplugInitError = ButtplugInitError;
class ButtplugDeviceError extends ButtplugError {
    constructor(message, id = Messages.SYSTEM_MESSAGE_ID) {
        super(message, Messages.ErrorClass.ERROR_DEVICE, id);
    }
}
exports.ButtplugDeviceError = ButtplugDeviceError;
class ButtplugMessageError extends ButtplugError {
    constructor(message, id = Messages.SYSTEM_MESSAGE_ID) {
        super(message, Messages.ErrorClass.ERROR_MSG, id);
    }
}
exports.ButtplugMessageError = ButtplugMessageError;
class ButtplugPingError extends ButtplugError {
    constructor(message, id = Messages.SYSTEM_MESSAGE_ID) {
        super(message, Messages.ErrorClass.ERROR_PING, id);
    }
}
exports.ButtplugPingError = ButtplugPingError;
class ButtplugUnknownError extends ButtplugError {
    constructor(message, id = Messages.SYSTEM_MESSAGE_ID) {
        super(message, Messages.ErrorClass.ERROR_UNKNOWN, id);
    }
}
exports.ButtplugUnknownError = ButtplugUnknownError;
//# sourceMappingURL=Exceptions.js.map