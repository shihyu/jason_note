import { EventEmitter } from 'eventemitter3';
import { ButtplugMessage } from '../core/Messages';

export declare class ButtplugBrowserWebsocketConnector extends EventEmitter {
    private _url;
    protected _ws: WebSocket | undefined;
    protected _websocketConstructor: typeof WebSocket | null;
    constructor(_url: string);
    get Connected(): boolean;
    connect: () => Promise<void>;
    disconnect: () => Promise<void>;
    sendMessage(msg: ButtplugMessage): void;
    initialize: () => Promise<void>;
    protected parseIncomingMessage(event: MessageEvent): void;
    protected onReaderLoad(event: Event): void;
}
