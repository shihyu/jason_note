"use strict";
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
exports.BPTestClient = void 0;
exports.SetupTestSuite = SetupTestSuite;
const index_1 = require("../src/index");
class BPTestClient extends index_1.ButtplugClient {
    constructor(ClientName) {
        super(ClientName);
    }
    get PingTimer() {
        return this._pingTimer;
    }
    sendMessage(msg) {
        const _super = Object.create(null, {
            sendMessage: { get: () => super.sendMessage }
        });
        return __awaiter(this, void 0, void 0, function* () {
            return _super.sendMessage.call(this, msg);
        });
    }
}
exports.BPTestClient = BPTestClient;
function SetupTestSuite() {
    // None of our tests should take very long.
    jest.setTimeout(1000);
    process.on("unhandledRejection", (reason, p) => {
        throw new Error(`Unhandled Promise rejection!\n---\n${reason.stack}\n---\n`);
    });
}
/*

export async function SetupTestServer(): Promise<{Client: ButtplugClient,
                                                  Server: ButtplugServer,
                                                  TestDeviceManager: TestDeviceSubtypeManager,
                                                  Connector: ButtplugEmbeddedClientConnector}> {
  const client = new ButtplugClient("Test Client");
  const server = new ButtplugServer("Test Server");
  server.ClearDeviceManagers();
  const testdevicemanager = new TestDeviceSubtypeManager();
  server.AddDeviceManager(testdevicemanager);
  const localConnector = new ButtplugEmbeddedClientConnector();
  localConnector.Server = server;
  await client.Connect(localConnector);
  return Promise.resolve({Client: client,
                          Server: server,
                          TestDeviceManager: testdevicemanager,
                          Connector: localConnector});
}
*/ 
//# sourceMappingURL=utils.js.map