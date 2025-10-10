/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
// tslint:disable:max-classes-per-file
'use strict';
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RawReading = exports.RawUnsubscribeCmd = exports.RawSubscribeCmd = exports.RawWriteCmd = exports.RawReadCmd = exports.SensorReading = exports.SensorReadCmd = exports.LinearCmd = exports.VectorSubcommand = exports.RotateCmd = exports.RotateSubcommand = exports.ScalarCmd = exports.ScalarSubcommand = exports.GenericMessageSubcommand = exports.StopAllDevices = exports.StopDeviceCmd = exports.ServerInfo = exports.RequestServerInfo = exports.ScanningFinished = exports.StopScanning = exports.StartScanning = exports.RequestDeviceList = exports.DeviceRemoved = exports.DeviceAdded = exports.DeviceList = exports.DeviceInfo = exports.Error = exports.ErrorClass = exports.Ping = exports.Ok = exports.ButtplugSystemMessage = exports.ButtplugDeviceMessage = exports.ButtplugMessage = exports.SensorDeviceMessageAttributes = exports.RawDeviceMessageAttributes = exports.GenericDeviceMessageAttributes = exports.SensorType = exports.ActuatorType = exports.MessageAttributes = exports.MESSAGE_SPEC_VERSION = exports.MAX_ID = exports.DEFAULT_MESSAGE_ID = exports.SYSTEM_MESSAGE_ID = void 0;
const class_transformer_1 = require("class-transformer");
require("reflect-metadata");
exports.SYSTEM_MESSAGE_ID = 0;
exports.DEFAULT_MESSAGE_ID = 1;
exports.MAX_ID = 4294967295;
exports.MESSAGE_SPEC_VERSION = 3;
class MessageAttributes {
    constructor(data) {
        Object.assign(this, data);
    }
    update() {
        var _a, _b, _c, _d, _e;
        (_a = this.ScalarCmd) === null || _a === void 0 ? void 0 : _a.forEach((x, i) => (x.Index = i));
        (_b = this.RotateCmd) === null || _b === void 0 ? void 0 : _b.forEach((x, i) => (x.Index = i));
        (_c = this.LinearCmd) === null || _c === void 0 ? void 0 : _c.forEach((x, i) => (x.Index = i));
        (_d = this.SensorReadCmd) === null || _d === void 0 ? void 0 : _d.forEach((x, i) => (x.Index = i));
        (_e = this.SensorSubscribeCmd) === null || _e === void 0 ? void 0 : _e.forEach((x, i) => (x.Index = i));
    }
}
exports.MessageAttributes = MessageAttributes;
var ActuatorType;
(function (ActuatorType) {
    ActuatorType["Unknown"] = "Unknown";
    ActuatorType["Vibrate"] = "Vibrate";
    ActuatorType["Rotate"] = "Rotate";
    ActuatorType["Oscillate"] = "Oscillate";
    ActuatorType["Constrict"] = "Constrict";
    ActuatorType["Inflate"] = "Inflate";
    ActuatorType["Position"] = "Position";
})(ActuatorType || (exports.ActuatorType = ActuatorType = {}));
var SensorType;
(function (SensorType) {
    SensorType["Unknown"] = "Unknown";
    SensorType["Battery"] = "Battery";
    SensorType["RSSI"] = "RSSI";
    SensorType["Button"] = "Button";
    SensorType["Pressure"] = "Pressure";
    // Temperature,
    // Accelerometer,
    // Gyro,
})(SensorType || (exports.SensorType = SensorType = {}));
class GenericDeviceMessageAttributes {
    constructor(data) {
        this.Index = 0;
        Object.assign(this, data);
    }
}
exports.GenericDeviceMessageAttributes = GenericDeviceMessageAttributes;
class RawDeviceMessageAttributes {
    constructor(Endpoints) {
        this.Endpoints = Endpoints;
    }
}
exports.RawDeviceMessageAttributes = RawDeviceMessageAttributes;
class SensorDeviceMessageAttributes {
    constructor(data) {
        this.Index = 0;
        Object.assign(this, data);
    }
}
exports.SensorDeviceMessageAttributes = SensorDeviceMessageAttributes;
class ButtplugMessage {
    constructor(Id) {
        this.Id = Id;
    }
    // tslint:disable-next-line:ban-types
    get Type() {
        return this.constructor;
    }
    toJSON() {
        return JSON.stringify(this.toProtocolFormat());
    }
    toProtocolFormat() {
        const jsonObj = {};
        jsonObj[this.constructor.Name] =
            (0, class_transformer_1.instanceToPlain)(this);
        return jsonObj;
    }
    update() { }
}
exports.ButtplugMessage = ButtplugMessage;
class ButtplugDeviceMessage extends ButtplugMessage {
    constructor(DeviceIndex, Id) {
        super(Id);
        this.DeviceIndex = DeviceIndex;
        this.Id = Id;
    }
}
exports.ButtplugDeviceMessage = ButtplugDeviceMessage;
class ButtplugSystemMessage extends ButtplugMessage {
    constructor(Id = exports.SYSTEM_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.ButtplugSystemMessage = ButtplugSystemMessage;
class Ok extends ButtplugSystemMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.Ok = Ok;
Ok.Name = 'Ok';
class Ping extends ButtplugMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.Ping = Ping;
Ping.Name = 'Ping';
var ErrorClass;
(function (ErrorClass) {
    ErrorClass[ErrorClass["ERROR_UNKNOWN"] = 0] = "ERROR_UNKNOWN";
    ErrorClass[ErrorClass["ERROR_INIT"] = 1] = "ERROR_INIT";
    ErrorClass[ErrorClass["ERROR_PING"] = 2] = "ERROR_PING";
    ErrorClass[ErrorClass["ERROR_MSG"] = 3] = "ERROR_MSG";
    ErrorClass[ErrorClass["ERROR_DEVICE"] = 4] = "ERROR_DEVICE";
})(ErrorClass || (exports.ErrorClass = ErrorClass = {}));
class Error extends ButtplugMessage {
    constructor(ErrorMessage, ErrorCode = ErrorClass.ERROR_UNKNOWN, Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.ErrorMessage = ErrorMessage;
        this.ErrorCode = ErrorCode;
        this.Id = Id;
    }
    get Schemversion() {
        return 0;
    }
}
exports.Error = Error;
Error.Name = 'Error';
class DeviceInfo {
    constructor(data) {
        Object.assign(this, data);
    }
}
exports.DeviceInfo = DeviceInfo;
__decorate([
    (0, class_transformer_1.Type)(() => MessageAttributes),
    __metadata("design:type", MessageAttributes)
], DeviceInfo.prototype, "DeviceMessages", void 0);
class DeviceList extends ButtplugMessage {
    constructor(devices, id = exports.DEFAULT_MESSAGE_ID) {
        super(id);
        this.Devices = devices;
        this.Id = id;
    }
    update() {
        for (const device of this.Devices) {
            device.DeviceMessages.update();
        }
    }
}
exports.DeviceList = DeviceList;
DeviceList.Name = 'DeviceList';
__decorate([
    (0, class_transformer_1.Type)(() => DeviceInfo),
    __metadata("design:type", Array)
], DeviceList.prototype, "Devices", void 0);
class DeviceAdded extends ButtplugSystemMessage {
    constructor(data) {
        super();
        Object.assign(this, data);
    }
    update() {
        this.DeviceMessages.update();
    }
}
exports.DeviceAdded = DeviceAdded;
DeviceAdded.Name = 'DeviceAdded';
__decorate([
    (0, class_transformer_1.Type)(() => MessageAttributes),
    __metadata("design:type", MessageAttributes)
], DeviceAdded.prototype, "DeviceMessages", void 0);
class DeviceRemoved extends ButtplugSystemMessage {
    constructor(DeviceIndex) {
        super();
        this.DeviceIndex = DeviceIndex;
    }
}
exports.DeviceRemoved = DeviceRemoved;
DeviceRemoved.Name = 'DeviceRemoved';
class RequestDeviceList extends ButtplugMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.RequestDeviceList = RequestDeviceList;
RequestDeviceList.Name = 'RequestDeviceList';
class StartScanning extends ButtplugMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.StartScanning = StartScanning;
StartScanning.Name = 'StartScanning';
class StopScanning extends ButtplugMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.StopScanning = StopScanning;
StopScanning.Name = 'StopScanning';
class ScanningFinished extends ButtplugSystemMessage {
    constructor() {
        super();
    }
}
exports.ScanningFinished = ScanningFinished;
ScanningFinished.Name = 'ScanningFinished';
class RequestServerInfo extends ButtplugMessage {
    constructor(ClientName, MessageVersion = 0, Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.ClientName = ClientName;
        this.MessageVersion = MessageVersion;
        this.Id = Id;
    }
}
exports.RequestServerInfo = RequestServerInfo;
RequestServerInfo.Name = 'RequestServerInfo';
class ServerInfo extends ButtplugSystemMessage {
    constructor(MessageVersion, MaxPingTime, ServerName, Id = exports.DEFAULT_MESSAGE_ID) {
        super();
        this.MessageVersion = MessageVersion;
        this.MaxPingTime = MaxPingTime;
        this.ServerName = ServerName;
        this.Id = Id;
    }
}
exports.ServerInfo = ServerInfo;
ServerInfo.Name = 'ServerInfo';
class StopDeviceCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex = -1, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Id = Id;
    }
}
exports.StopDeviceCmd = StopDeviceCmd;
StopDeviceCmd.Name = 'StopDeviceCmd';
class StopAllDevices extends ButtplugMessage {
    constructor(Id = exports.DEFAULT_MESSAGE_ID) {
        super(Id);
        this.Id = Id;
    }
}
exports.StopAllDevices = StopAllDevices;
StopAllDevices.Name = 'StopAllDevices';
class GenericMessageSubcommand {
    constructor(Index) {
        this.Index = Index;
    }
}
exports.GenericMessageSubcommand = GenericMessageSubcommand;
class ScalarSubcommand extends GenericMessageSubcommand {
    constructor(Index, Scalar, ActuatorType) {
        super(Index);
        this.Scalar = Scalar;
        this.ActuatorType = ActuatorType;
    }
}
exports.ScalarSubcommand = ScalarSubcommand;
class ScalarCmd extends ButtplugDeviceMessage {
    constructor(Scalars, DeviceIndex = -1, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.Scalars = Scalars;
        this.DeviceIndex = DeviceIndex;
        this.Id = Id;
    }
}
exports.ScalarCmd = ScalarCmd;
ScalarCmd.Name = 'ScalarCmd';
class RotateSubcommand extends GenericMessageSubcommand {
    constructor(Index, Speed, Clockwise) {
        super(Index);
        this.Speed = Speed;
        this.Clockwise = Clockwise;
    }
}
exports.RotateSubcommand = RotateSubcommand;
class RotateCmd extends ButtplugDeviceMessage {
    static Create(deviceIndex, commands) {
        const cmdList = new Array();
        let i = 0;
        for (const [speed, clockwise] of commands) {
            cmdList.push(new RotateSubcommand(i, speed, clockwise));
            ++i;
        }
        return new RotateCmd(cmdList, deviceIndex);
    }
    constructor(Rotations, DeviceIndex = -1, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.Rotations = Rotations;
        this.DeviceIndex = DeviceIndex;
        this.Id = Id;
    }
}
exports.RotateCmd = RotateCmd;
RotateCmd.Name = 'RotateCmd';
class VectorSubcommand extends GenericMessageSubcommand {
    constructor(Index, Position, Duration) {
        super(Index);
        this.Position = Position;
        this.Duration = Duration;
    }
}
exports.VectorSubcommand = VectorSubcommand;
class LinearCmd extends ButtplugDeviceMessage {
    static Create(deviceIndex, commands) {
        const cmdList = new Array();
        let i = 0;
        for (const cmd of commands) {
            cmdList.push(new VectorSubcommand(i, cmd[0], cmd[1]));
            ++i;
        }
        return new LinearCmd(cmdList, deviceIndex);
    }
    constructor(Vectors, DeviceIndex = -1, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.Vectors = Vectors;
        this.DeviceIndex = DeviceIndex;
        this.Id = Id;
    }
}
exports.LinearCmd = LinearCmd;
LinearCmd.Name = 'LinearCmd';
class SensorReadCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex, SensorIndex, SensorType, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.SensorIndex = SensorIndex;
        this.SensorType = SensorType;
        this.Id = Id;
    }
}
exports.SensorReadCmd = SensorReadCmd;
SensorReadCmd.Name = 'SensorReadCmd';
class SensorReading extends ButtplugDeviceMessage {
    constructor(DeviceIndex, SensorIndex, SensorType, Data, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.SensorIndex = SensorIndex;
        this.SensorType = SensorType;
        this.Data = Data;
        this.Id = Id;
    }
}
exports.SensorReading = SensorReading;
SensorReading.Name = 'SensorReading';
class RawReadCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex, Endpoint, ExpectedLength, Timeout, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Endpoint = Endpoint;
        this.ExpectedLength = ExpectedLength;
        this.Timeout = Timeout;
        this.Id = Id;
    }
}
exports.RawReadCmd = RawReadCmd;
RawReadCmd.Name = 'RawReadCmd';
class RawWriteCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex, Endpoint, Data, WriteWithResponse, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Endpoint = Endpoint;
        this.Data = Data;
        this.WriteWithResponse = WriteWithResponse;
        this.Id = Id;
    }
}
exports.RawWriteCmd = RawWriteCmd;
RawWriteCmd.Name = 'RawWriteCmd';
class RawSubscribeCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex, Endpoint, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Endpoint = Endpoint;
        this.Id = Id;
    }
}
exports.RawSubscribeCmd = RawSubscribeCmd;
RawSubscribeCmd.Name = 'RawSubscribeCmd';
class RawUnsubscribeCmd extends ButtplugDeviceMessage {
    constructor(DeviceIndex, Endpoint, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Endpoint = Endpoint;
        this.Id = Id;
    }
}
exports.RawUnsubscribeCmd = RawUnsubscribeCmd;
RawUnsubscribeCmd.Name = 'RawUnsubscribeCmd';
class RawReading extends ButtplugDeviceMessage {
    constructor(DeviceIndex, Endpoint, Data, Id = exports.DEFAULT_MESSAGE_ID) {
        super(DeviceIndex, Id);
        this.DeviceIndex = DeviceIndex;
        this.Endpoint = Endpoint;
        this.Data = Data;
        this.Id = Id;
    }
}
exports.RawReading = RawReading;
RawReading.Name = 'RawReading';
//# sourceMappingURL=Messages.js.map