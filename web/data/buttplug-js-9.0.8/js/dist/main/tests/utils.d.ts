import { ButtplugClient } from "../src/index";
import * as Messages from "../src/core/Messages";
export declare class BPTestClient extends ButtplugClient {
    constructor(ClientName: string);
    get PingTimer(): NodeJS.Timeout | null;
    sendMessage(msg: Messages.ButtplugMessage): Promise<Messages.ButtplugMessage>;
}
export declare function SetupTestSuite(): void;
