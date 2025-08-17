import { ButtplugMessage } from '../core/Messages';
import { EventEmitter } from 'eventemitter3';

export interface IButtplugClientConnector extends EventEmitter {
    connect: () => Promise<void>;
    disconnect: () => Promise<void>;
    initialize: () => Promise<void>;
    send: (msg: ButtplugMessage) => void;
    readonly Connected: boolean;
}
