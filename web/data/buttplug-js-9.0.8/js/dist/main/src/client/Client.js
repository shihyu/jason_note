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
exports.ButtplugClient = void 0;
const Logging_1 = require("../core/Logging");
const eventemitter3_1 = require("eventemitter3");
const ButtplugClientDevice_1 = require("./ButtplugClientDevice");
const ButtplugMessageSorter_1 = require("../utils/ButtplugMessageSorter");
const Messages = __importStar(require("../core/Messages"));
const Exceptions_1 = require("../core/Exceptions");
const ButtplugClientConnectorException_1 = require("./ButtplugClientConnectorException");
const MessageUtils_1 = require("../core/MessageUtils");
class ButtplugClient extends eventemitter3_1.EventEmitter {
    constructor(clientName = 'Generic Buttplug Client') {
        super();
        this._pingTimer = null;
        this._connector = null;
        this._devices = new Map();
        this._logger = Logging_1.ButtplugLogger.Logger;
        this._isScanning = false;
        this._sorter = new ButtplugMessageSorter_1.ButtplugMessageSorter(true);
        this.connect = (connector) => __awaiter(this, void 0, void 0, function* () {
            this._logger.Info(`ButtplugClient: Connecting using ${connector.constructor.name}`);
            yield connector.connect();
            this._connector = connector;
            this._connector.addListener('message', this.parseMessages);
            this._connector.addListener('disconnect', this.disconnectHandler);
            yield this.initializeConnection();
        });
        this.disconnect = () => __awaiter(this, void 0, void 0, function* () {
            this._logger.Debug('ButtplugClient: Disconnect called');
            this.checkConnector();
            yield this.shutdownConnection();
            yield this._connector.disconnect();
        });
        this.startScanning = () => __awaiter(this, void 0, void 0, function* () {
            this._logger.Debug('ButtplugClient: StartScanning called');
            this._isScanning = true;
            yield this.sendMsgExpectOk(new Messages.StartScanning());
        });
        this.stopScanning = () => __awaiter(this, void 0, void 0, function* () {
            this._logger.Debug('ButtplugClient: StopScanning called');
            this._isScanning = false;
            yield this.sendMsgExpectOk(new Messages.StopScanning());
        });
        this.stopAllDevices = () => __awaiter(this, void 0, void 0, function* () {
            this._logger.Debug('ButtplugClient: StopAllDevices');
            yield this.sendMsgExpectOk(new Messages.StopAllDevices());
        });
        this.disconnectHandler = () => {
            this._logger.Info('ButtplugClient: Disconnect event receieved.');
            this.emit('disconnect');
        };
        this.parseMessages = (msgs) => {
            const leftoverMsgs = this._sorter.ParseIncomingMessages(msgs);
            for (const x of leftoverMsgs) {
                switch ((0, MessageUtils_1.getMessageClassFromMessage)(x)) {
                    case Messages.DeviceAdded: {
                        const addedMsg = x;
                        const addedDevice = ButtplugClientDevice_1.ButtplugClientDevice.fromMsg(addedMsg, this.sendDeviceMessageClosure);
                        this._devices.set(addedMsg.DeviceIndex, addedDevice);
                        this.emit('deviceadded', addedDevice);
                        break;
                    }
                    case Messages.DeviceRemoved: {
                        const removedMsg = x;
                        if (this._devices.has(removedMsg.DeviceIndex)) {
                            const removedDevice = this._devices.get(removedMsg.DeviceIndex);
                            removedDevice === null || removedDevice === void 0 ? void 0 : removedDevice.emitDisconnected();
                            this._devices.delete(removedMsg.DeviceIndex);
                            this.emit('deviceremoved', removedDevice);
                        }
                        break;
                    }
                    case Messages.ScanningFinished:
                        this._isScanning = false;
                        this.emit('scanningfinished', x);
                        break;
                }
            }
        };
        this.initializeConnection = () => __awaiter(this, void 0, void 0, function* () {
            this.checkConnector();
            const msg = yield this.sendMessage(new Messages.RequestServerInfo(this._clientName, Messages.MESSAGE_SPEC_VERSION));
            switch ((0, MessageUtils_1.getMessageClassFromMessage)(msg)) {
                case Messages.ServerInfo: {
                    const serverinfo = msg;
                    this._logger.Info(`ButtplugClient: Connected to Server ${serverinfo.ServerName}`);
                    // TODO: maybe store server name, do something with message template version?
                    const ping = serverinfo.MaxPingTime;
                    if (serverinfo.MessageVersion < Messages.MESSAGE_SPEC_VERSION) {
                        // Disconnect and throw an exception explaining the version mismatch problem.
                        yield this._connector.disconnect();
                        throw Exceptions_1.ButtplugError.LogAndError(Exceptions_1.ButtplugInitError, this._logger, `Server protocol version ${serverinfo.MessageVersion} is older than client protocol version ${Messages.MESSAGE_SPEC_VERSION}. Please update server.`);
                    }
                    if (ping > 0) {
                        /*
                        this._pingTimer = setInterval(async () => {
                          // If we've disconnected, stop trying to ping the server.
                          if (!this.Connected) {
                            await this.ShutdownConnection();
                            return;
                          }
                          await this.SendMessage(new Messages.Ping());
                        } , Math.round(ping / 2));
                        */
                    }
                    yield this.requestDeviceList();
                    return true;
                }
                case Messages.Error: {
                    // Disconnect and throw an exception with the error message we got back.
                    // This will usually only error out if we have a version mismatch that the
                    // server has detected.
                    yield this._connector.disconnect();
                    const err = msg;
                    throw Exceptions_1.ButtplugError.LogAndError(Exceptions_1.ButtplugInitError, this._logger, `Cannot connect to server. ${err.ErrorMessage}`);
                }
            }
            return false;
        });
        this.requestDeviceList = () => __awaiter(this, void 0, void 0, function* () {
            this.checkConnector();
            this._logger.Debug('ButtplugClient: ReceiveDeviceList called');
            const deviceList = (yield this.sendMessage(new Messages.RequestDeviceList()));
            deviceList.Devices.forEach((d) => {
                if (!this._devices.has(d.DeviceIndex)) {
                    const device = ButtplugClientDevice_1.ButtplugClientDevice.fromMsg(d, this.sendDeviceMessageClosure);
                    this._logger.Debug(`ButtplugClient: Adding Device: ${device}`);
                    this._devices.set(d.DeviceIndex, device);
                    this.emit('deviceadded', device);
                }
                else {
                    this._logger.Debug(`ButtplugClient: Device already added: ${d}`);
                }
            });
        });
        this.shutdownConnection = () => __awaiter(this, void 0, void 0, function* () {
            yield this.stopAllDevices();
            if (this._pingTimer !== null) {
                clearInterval(this._pingTimer);
                this._pingTimer = null;
            }
        });
        this.sendMsgExpectOk = (msg) => __awaiter(this, void 0, void 0, function* () {
            const response = yield this.sendMessage(msg);
            switch ((0, MessageUtils_1.getMessageClassFromMessage)(response)) {
                case Messages.Ok:
                    return;
                case Messages.Error:
                    throw Exceptions_1.ButtplugError.FromError(response);
                default:
                    throw Exceptions_1.ButtplugError.LogAndError(Exceptions_1.ButtplugMessageError, this._logger, `Message type ${(0, MessageUtils_1.getMessageClassFromMessage)(response).constructor} not handled by SendMsgExpectOk`);
            }
        });
        this.sendDeviceMessageClosure = (device, msg) => __awaiter(this, void 0, void 0, function* () {
            return yield this.sendDeviceMessage(device, msg);
        });
        this._clientName = clientName;
        this._logger.Debug(`ButtplugClient: Client ${clientName} created.`);
    }
    get connected() {
        return this._connector !== null && this._connector.Connected;
    }
    get devices() {
        // While this function doesn't actually send a message, if we don't have a
        // connector, we shouldn't have devices.
        this.checkConnector();
        const devices = [];
        this._devices.forEach((d) => {
            devices.push(d);
        });
        return devices;
    }
    get isScanning() {
        return this._isScanning;
    }
    sendDeviceMessage(device, deviceMsg) {
        return __awaiter(this, void 0, void 0, function* () {
            this.checkConnector();
            const dev = this._devices.get(device.index);
            if (dev === undefined) {
                throw Exceptions_1.ButtplugError.LogAndError(Exceptions_1.ButtplugDeviceError, this._logger, `Device ${device.index} not available.`);
            }
            deviceMsg.DeviceIndex = device.index;
            return yield this.sendMessage(deviceMsg);
        });
    }
    sendMessage(msg) {
        return __awaiter(this, void 0, void 0, function* () {
            this.checkConnector();
            const p = this._sorter.PrepareOutgoingMessage(msg);
            yield this._connector.send(msg);
            return yield p;
        });
    }
    checkConnector() {
        if (!this.connected) {
            throw new ButtplugClientConnectorException_1.ButtplugClientConnectorException('ButtplugClient not connected');
        }
    }
}
exports.ButtplugClient = ButtplugClient;
//# sourceMappingURL=Client.js.map