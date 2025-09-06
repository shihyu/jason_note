import { ButtplugBrowserWebsocketClientConnector } from './ButtplugBrowserWebsocketClientConnector';

export declare class ButtplugNodeWebsocketClientConnector extends ButtplugBrowserWebsocketClientConnector {
    protected _websocketConstructor: {
        new (url: string | URL, protocols?: string | string[] | undefined): WebSocket;
        prototype: WebSocket;
        readonly CONNECTING: 0;
        readonly OPEN: 1;
        readonly CLOSING: 2;
        readonly CLOSED: 3;
    };
}
