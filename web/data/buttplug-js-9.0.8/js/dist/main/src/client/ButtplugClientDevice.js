/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
'use strict';
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
exports.ButtplugClientDevice = void 0;
const Messages = __importStar(require("../core/Messages"));
const Exceptions_1 = require("../core/Exceptions");
const eventemitter3_1 = require("eventemitter3");
const MessageUtils_1 = require("../core/MessageUtils");
/**
 * Represents an abstract device, capable of taking certain kinds of messages.
 */
class ButtplugClientDevice extends eventemitter3_1.EventEmitter {
    /**
     * Return the name of the device.
     */
    get name() {
        return this._deviceInfo.DeviceName;
    }
    /**
     * Return the user set name of the device.
     */
    get displayName() {
        return this._deviceInfo.DeviceDisplayName;
    }
    /**
     * Return the index of the device.
     */
    get index() {
        return this._deviceInfo.DeviceIndex;
    }
    /**
     * Return the index of the device.
     */
    get messageTimingGap() {
        return this._deviceInfo.DeviceMessageTimingGap;
    }
    /**
     * Return a list of message types the device accepts.
     */
    get messageAttributes() {
        return this._deviceInfo.DeviceMessages;
    }
    static fromMsg(msg, sendClosure) {
        return new ButtplugClientDevice(msg, sendClosure);
    }
    /**
     * @param _index Index of the device, as created by the device manager.
     * @param _name Name of the device.
     * @param allowedMsgs Buttplug messages the device can receive.
     */
    constructor(_deviceInfo, _sendClosure) {
        super();
        this._deviceInfo = _deviceInfo;
        this._sendClosure = _sendClosure;
        // Map of messages and their attributes (feature count, etc...)
        this.allowedMsgs = new Map();
        _deviceInfo.DeviceMessages.update();
    }
    send(msg) {
        return __awaiter(this, void 0, void 0, function* () {
            // Assume we're getting the closure from ButtplugClient, which does all of
            // the index/existence/connection/message checks for us.
            return yield this._sendClosure(this, msg);
        });
    }
    sendExpectOk(msg) {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield this.send(msg);
            switch ((0, MessageUtils_1.getMessageClassFromMessage)(response)) {
                case Messages.Ok:
                    return;
                case Messages.Error:
                    throw Exceptions_1.ButtplugError.FromError(response);
                default:
                    throw new Exceptions_1.ButtplugMessageError(`Message type ${response.constructor} not handled by SendMsgExpectOk`);
            }
        });
    }
    scalar(scalar) {
        return __awaiter(this, void 0, void 0, function* () {
            if (Array.isArray(scalar)) {
                yield this.sendExpectOk(new Messages.ScalarCmd(scalar, this.index));
            }
            else {
                yield this.sendExpectOk(new Messages.ScalarCmd([scalar], this.index));
            }
        });
    }
    scalarCommandBuilder(speed, actuator) {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            const scalarAttrs = (_a = this.messageAttributes.ScalarCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.ActuatorType === actuator);
            if (!scalarAttrs || scalarAttrs.length === 0) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no ${actuator} capabilities`);
            }
            const cmds = [];
            if (typeof speed === 'number') {
                scalarAttrs.forEach((x) => cmds.push(new Messages.ScalarSubcommand(x.Index, speed, actuator)));
            }
            else if (Array.isArray(speed)) {
                if (speed.length > scalarAttrs.length) {
                    throw new Exceptions_1.ButtplugDeviceError(`${speed.length} commands send to a device with ${scalarAttrs.length} vibrators`);
                }
                scalarAttrs.forEach((x, i) => {
                    cmds.push(new Messages.ScalarSubcommand(x.Index, speed[i], actuator));
                });
            }
            else {
                throw new Exceptions_1.ButtplugDeviceError(`${actuator} can only take numbers or arrays of numbers.`);
            }
            yield this.scalar(cmds);
        });
    }
    get vibrateAttributes() {
        var _a, _b;
        return ((_b = (_a = this.messageAttributes.ScalarCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.ActuatorType === Messages.ActuatorType.Vibrate)) !== null && _b !== void 0 ? _b : []);
    }
    vibrate(speed) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.scalarCommandBuilder(speed, Messages.ActuatorType.Vibrate);
        });
    }
    get oscillateAttributes() {
        var _a, _b;
        return ((_b = (_a = this.messageAttributes.ScalarCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.ActuatorType === Messages.ActuatorType.Oscillate)) !== null && _b !== void 0 ? _b : []);
    }
    oscillate(speed) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.scalarCommandBuilder(speed, Messages.ActuatorType.Oscillate);
        });
    }
    get rotateAttributes() {
        var _a;
        return (_a = this.messageAttributes.RotateCmd) !== null && _a !== void 0 ? _a : [];
    }
    rotate(values, clockwise) {
        return __awaiter(this, void 0, void 0, function* () {
            const rotateAttrs = this.messageAttributes.RotateCmd;
            if (!rotateAttrs || rotateAttrs.length === 0) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no Rotate capabilities`);
            }
            let msg;
            if (typeof values === 'number') {
                msg = Messages.RotateCmd.Create(this.index, new Array(rotateAttrs.length).fill([values, clockwise]));
            }
            else if (Array.isArray(values)) {
                msg = Messages.RotateCmd.Create(this.index, values);
            }
            else {
                throw new Exceptions_1.ButtplugDeviceError('SendRotateCmd can only take a number and boolean, or an array of number/boolean tuples');
            }
            yield this.sendExpectOk(msg);
        });
    }
    get linearAttributes() {
        var _a;
        return (_a = this.messageAttributes.LinearCmd) !== null && _a !== void 0 ? _a : [];
    }
    linear(values, duration) {
        return __awaiter(this, void 0, void 0, function* () {
            const linearAttrs = this.messageAttributes.LinearCmd;
            if (!linearAttrs || linearAttrs.length === 0) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no Linear capabilities`);
            }
            let msg;
            if (typeof values === 'number') {
                msg = Messages.LinearCmd.Create(this.index, new Array(linearAttrs.length).fill([values, duration]));
            }
            else if (Array.isArray(values)) {
                msg = Messages.LinearCmd.Create(this.index, values);
            }
            else {
                throw new Exceptions_1.ButtplugDeviceError('SendLinearCmd can only take a number and number, or an array of number/number tuples');
            }
            yield this.sendExpectOk(msg);
        });
    }
    sensorRead(sensorIndex, sensorType) {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield this.send(new Messages.SensorReadCmd(this.index, sensorIndex, sensorType));
            switch ((0, MessageUtils_1.getMessageClassFromMessage)(response)) {
                case Messages.SensorReading:
                    return response.Data;
                case Messages.Error:
                    throw Exceptions_1.ButtplugError.FromError(response);
                default:
                    throw new Exceptions_1.ButtplugMessageError(`Message type ${response.constructor} not handled by sensorRead`);
            }
        });
    }
    get hasBattery() {
        var _a;
        const batteryAttrs = (_a = this.messageAttributes.SensorReadCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.SensorType === Messages.SensorType.Battery);
        return batteryAttrs !== undefined && batteryAttrs.length > 0;
    }
    battery() {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            if (!this.hasBattery) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no Battery capabilities`);
            }
            const batteryAttrs = (_a = this.messageAttributes.SensorReadCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.SensorType === Messages.SensorType.Battery);
            // Find the battery sensor, we'll need its index.
            const result = yield this.sensorRead(batteryAttrs[0].Index, Messages.SensorType.Battery);
            return result[0] / 100.0;
        });
    }
    get hasRssi() {
        var _a;
        const rssiAttrs = (_a = this.messageAttributes.SensorReadCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.SensorType === Messages.SensorType.RSSI);
        return rssiAttrs !== undefined && rssiAttrs.length === 0;
    }
    rssi() {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            if (!this.hasRssi) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no RSSI capabilities`);
            }
            const rssiAttrs = (_a = this.messageAttributes.SensorReadCmd) === null || _a === void 0 ? void 0 : _a.filter((x) => x.SensorType === Messages.SensorType.RSSI);
            // Find the battery sensor, we'll need its index.
            const result = yield this.sensorRead(rssiAttrs[0].Index, Messages.SensorType.RSSI);
            return result[0];
        });
    }
    rawRead(endpoint, expectedLength, timeout) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.messageAttributes.RawReadCmd) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw read capabilities`);
            }
            if (this.messageAttributes.RawReadCmd.Endpoints.indexOf(endpoint) === -1) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw readable endpoint ${endpoint}`);
            }
            const response = yield this.send(new Messages.RawReadCmd(this.index, endpoint, expectedLength, timeout));
            switch ((0, MessageUtils_1.getMessageClassFromMessage)(response)) {
                case Messages.RawReading:
                    return new Uint8Array(response.Data);
                case Messages.Error:
                    throw Exceptions_1.ButtplugError.FromError(response);
                default:
                    throw new Exceptions_1.ButtplugMessageError(`Message type ${response.constructor} not handled by rawRead`);
            }
        });
    }
    rawWrite(endpoint, data, writeWithResponse) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.messageAttributes.RawWriteCmd) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw write capabilities`);
            }
            if (this.messageAttributes.RawWriteCmd.Endpoints.indexOf(endpoint) === -1) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw writable endpoint ${endpoint}`);
            }
            yield this.sendExpectOk(new Messages.RawWriteCmd(this.index, endpoint, data, writeWithResponse));
        });
    }
    rawSubscribe(endpoint) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.messageAttributes.RawSubscribeCmd) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw subscribe capabilities`);
            }
            if (this.messageAttributes.RawSubscribeCmd.Endpoints.indexOf(endpoint) === -1) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw subscribable endpoint ${endpoint}`);
            }
            yield this.sendExpectOk(new Messages.RawSubscribeCmd(this.index, endpoint));
        });
    }
    rawUnsubscribe(endpoint) {
        return __awaiter(this, void 0, void 0, function* () {
            // This reuses raw subscribe's info.
            if (!this.messageAttributes.RawSubscribeCmd) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw unsubscribe capabilities`);
            }
            if (this.messageAttributes.RawSubscribeCmd.Endpoints.indexOf(endpoint) === -1) {
                throw new Exceptions_1.ButtplugDeviceError(`Device ${this.name} has no raw unsubscribable endpoint ${endpoint}`);
            }
            yield this.sendExpectOk(new Messages.RawUnsubscribeCmd(this.index, endpoint));
        });
    }
    stop() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.sendExpectOk(new Messages.StopDeviceCmd(this.index));
        });
    }
    emitDisconnected() {
        this.emit('deviceremoved');
    }
}
exports.ButtplugClientDevice = ButtplugClientDevice;
//# sourceMappingURL=ButtplugClientDevice.js.map