import { IButtplugClientConnector } from './IButtplugClientConnector';
import { ButtplugMessage } from '../core/Messages';
import { ButtplugBrowserWebsocketConnector } from '../utils/ButtplugBrowserWebsocketConnector';

export declare class ButtplugBrowserWebsocketClientConnector extends ButtplugBrowserWebsocketConnector implements IButtplugClientConnector {
    send: (msg: ButtplugMessage) => void;
}
