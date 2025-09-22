import { ButtplugBrowserWebsocketClientConnector } from './ButtplugBrowserWebsocketClientConnector';

export declare class ButtplugNodeWebsocketClientConnector extends ButtplugBrowserWebsocketClientConnector {
    protected _websocketConstructor: typeof WebSocket;
}
