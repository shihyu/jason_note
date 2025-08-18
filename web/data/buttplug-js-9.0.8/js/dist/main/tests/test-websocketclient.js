"use strict";
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
const mock_socket_1 = require("mock-socket");
const Client_1 = require("../src/client/Client");
const Messages = __importStar(require("../src/core/Messages"));
const MessageUtils_1 = require("../src/core/MessageUtils");
const utils_1 = require("./utils");
const src_1 = require("../src");
(0, utils_1.SetupTestSuite)();
describe("Websocket Client Tests", () => {
    let mockServer;
    let socket;
    let bp;
    let p;
    let res;
    let rej;
    class BPTestClient extends Client_1.ButtplugClient {
        constructor(ClientName) {
            super(ClientName);
        }
        get PingTimer() {
            return this._pingTimer;
        }
    }
    beforeEach(() => __awaiter(void 0, void 0, void 0, function* () {
        mockServer = new mock_socket_1.Server("ws://localhost:6868");
        p = new Promise((resolve, reject) => { res = resolve; rej = reject; });
        const serverInfo = (jsonmsg) => {
            const msg = (0, MessageUtils_1.fromJSON)(jsonmsg)[0];
            if (msg.Type === Messages.RequestServerInfo) {
                delaySend(new Messages.ServerInfo(3, 0, "Test Server", msg.Id));
            }
            if (msg.Type === Messages.RequestDeviceList) {
                delaySend(new Messages.DeviceList([], msg.Id));
                // (socket as any).removeListener("message", serverInfo);
            }
        };
        mockServer.on("connection", (connectedSocket) => {
            socket = connectedSocket;
            // TODO Bug in typescript defs for mock-socket 8 means we can't use the
            // socket type as it was meant. See
            // https://github.com/thoov/mock-socket/issues/224
            socket.on("message", (data) => serverInfo(data));
        });
        bp = new Client_1.ButtplugClient("Test Buttplug Client");
        yield bp.connect(new src_1.ButtplugBrowserWebsocketClientConnector("ws://localhost:6868"));
    }));
    afterEach(function (done) {
        mockServer.stop(done);
    });
    function delaySend(msg) {
        process.nextTick(() => socket.send("[" + msg.toJSON() + "]"));
    }
    it("Should deal with request/reply correctly", () => __awaiter(void 0, void 0, void 0, function* () {
        socket.on("message", (jsonmsg) => {
            const msg = (0, MessageUtils_1.fromJSON)(jsonmsg)[0];
            delaySend(new Messages.Ok(msg.Id));
        });
        yield bp.startScanning();
        yield bp.stopScanning();
    }));
    it("Should receive disconnect event on websocket disconnect", () => __awaiter(void 0, void 0, void 0, function* () {
        bp.addListener("disconnect", () => { res(); });
        mockServer.close();
        return p;
    }));
    it("Should throw Error on return of error message", () => __awaiter(void 0, void 0, void 0, function* () {
        socket.on("message", (jsonmsg) => {
            const msg = (0, MessageUtils_1.fromJSON)(jsonmsg)[0];
            if (msg.Type === Messages.StopAllDevices) {
                delaySend(new Messages.Error("Error", Messages.ErrorClass.ERROR_MSG, msg.Id));
            }
        });
        yield expect(bp.stopAllDevices()).rejects.toBeInstanceOf(src_1.ButtplugMessageError);
    }));
    it("Should throw Error on TCPCONNECTREFUSED", () => __awaiter(void 0, void 0, void 0, function* () {
        const connector = new src_1.ButtplugBrowserWebsocketClientConnector("ws://localhost:31000");
        try {
            yield connector.connect();
        }
        catch (e) {
            expect(e).toBeDefined();
        }
    }));
});
//# sourceMappingURL=test-websocketclient.js.map