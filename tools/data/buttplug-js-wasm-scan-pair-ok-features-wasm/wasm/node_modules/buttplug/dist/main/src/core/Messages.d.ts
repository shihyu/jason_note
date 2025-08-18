/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
import 'reflect-metadata';
export declare const SYSTEM_MESSAGE_ID = 0;
export declare const DEFAULT_MESSAGE_ID = 1;
export declare const MAX_ID = 4294967295;
export declare const MESSAGE_SPEC_VERSION = 3;
export declare class MessageAttributes {
    ScalarCmd?: Array<GenericDeviceMessageAttributes>;
    RotateCmd?: Array<GenericDeviceMessageAttributes>;
    LinearCmd?: Array<GenericDeviceMessageAttributes>;
    RawReadCmd?: RawDeviceMessageAttributes;
    RawWriteCmd?: RawDeviceMessageAttributes;
    RawSubscribeCmd?: RawDeviceMessageAttributes;
    SensorReadCmd?: Array<SensorDeviceMessageAttributes>;
    SensorSubscribeCmd?: Array<SensorDeviceMessageAttributes>;
    StopDeviceCmd: {};
    constructor(data: Partial<MessageAttributes>);
    update(): void;
}
export declare enum ActuatorType {
    Unknown = "Unknown",
    Vibrate = "Vibrate",
    Rotate = "Rotate",
    Oscillate = "Oscillate",
    Constrict = "Constrict",
    Inflate = "Inflate",
    Position = "Position"
}
export declare enum SensorType {
    Unknown = "Unknown",
    Battery = "Battery",
    RSSI = "RSSI",
    Button = "Button",
    Pressure = "Pressure"
}
export declare class GenericDeviceMessageAttributes {
    FeatureDescriptor: string;
    ActuatorType: ActuatorType;
    StepCount: number;
    Index: number;
    constructor(data: Partial<GenericDeviceMessageAttributes>);
}
export declare class RawDeviceMessageAttributes {
    Endpoints: Array<string>;
    constructor(Endpoints: Array<string>);
}
export declare class SensorDeviceMessageAttributes {
    FeatureDescriptor: string;
    SensorType: SensorType;
    StepRange: Array<number>;
    Index: number;
    constructor(data: Partial<GenericDeviceMessageAttributes>);
}
export declare abstract class ButtplugMessage {
    Id: number;
    constructor(Id: number);
    get Type(): Function;
    toJSON(): string;
    toProtocolFormat(): object;
    update(): void;
}
export declare abstract class ButtplugDeviceMessage extends ButtplugMessage {
    DeviceIndex: number;
    Id: number;
    constructor(DeviceIndex: number, Id: number);
}
export declare abstract class ButtplugSystemMessage extends ButtplugMessage {
    Id: number;
    constructor(Id?: number);
}
export declare class Ok extends ButtplugSystemMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare class Ping extends ButtplugMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare enum ErrorClass {
    ERROR_UNKNOWN = 0,
    ERROR_INIT = 1,
    ERROR_PING = 2,
    ERROR_MSG = 3,
    ERROR_DEVICE = 4
}
export declare class Error extends ButtplugMessage {
    ErrorMessage: string;
    ErrorCode: ErrorClass;
    Id: number;
    static Name: string;
    constructor(ErrorMessage: string, ErrorCode?: ErrorClass, Id?: number);
    get Schemversion(): number;
}
export declare class DeviceInfo {
    DeviceIndex: number;
    DeviceName: string;
    DeviceMessages: MessageAttributes;
    DeviceDisplayName?: string;
    DeviceMessageTimingGap?: number;
    constructor(data: Partial<DeviceInfo>);
}
export declare class DeviceList extends ButtplugMessage {
    static Name: string;
    Devices: DeviceInfo[];
    Id: number;
    constructor(devices: DeviceInfo[], id?: number);
    update(): void;
}
export declare class DeviceAdded extends ButtplugSystemMessage {
    static Name: string;
    DeviceIndex: number;
    DeviceName: string;
    DeviceMessages: MessageAttributes;
    DeviceDisplayName?: string;
    DeviceMessageTimingGap?: number;
    constructor(data: Partial<DeviceAdded>);
    update(): void;
}
export declare class DeviceRemoved extends ButtplugSystemMessage {
    DeviceIndex: number;
    static Name: string;
    constructor(DeviceIndex: number);
}
export declare class RequestDeviceList extends ButtplugMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare class StartScanning extends ButtplugMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare class StopScanning extends ButtplugMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare class ScanningFinished extends ButtplugSystemMessage {
    static Name: string;
    constructor();
}
export declare class RequestServerInfo extends ButtplugMessage {
    ClientName: string;
    MessageVersion: number;
    Id: number;
    static Name: string;
    constructor(ClientName: string, MessageVersion?: number, Id?: number);
}
export declare class ServerInfo extends ButtplugSystemMessage {
    MessageVersion: number;
    MaxPingTime: number;
    ServerName: string;
    Id: number;
    static Name: string;
    constructor(MessageVersion: number, MaxPingTime: number, ServerName: string, Id?: number);
}
export declare class StopDeviceCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Id: number;
    static Name: string;
    constructor(DeviceIndex?: number, Id?: number);
}
export declare class StopAllDevices extends ButtplugMessage {
    Id: number;
    static Name: string;
    constructor(Id?: number);
}
export declare class GenericMessageSubcommand {
    Index: number;
    protected constructor(Index: number);
}
export declare class ScalarSubcommand extends GenericMessageSubcommand {
    Scalar: number;
    ActuatorType: ActuatorType;
    constructor(Index: number, Scalar: number, ActuatorType: ActuatorType);
}
export declare class ScalarCmd extends ButtplugDeviceMessage {
    Scalars: ScalarSubcommand[];
    DeviceIndex: number;
    Id: number;
    static Name: string;
    constructor(Scalars: ScalarSubcommand[], DeviceIndex?: number, Id?: number);
}
export declare class RotateSubcommand extends GenericMessageSubcommand {
    Speed: number;
    Clockwise: boolean;
    constructor(Index: number, Speed: number, Clockwise: boolean);
}
export declare class RotateCmd extends ButtplugDeviceMessage {
    Rotations: RotateSubcommand[];
    DeviceIndex: number;
    Id: number;
    static Name: string;
    static Create(deviceIndex: number, commands: [number, boolean][]): RotateCmd;
    constructor(Rotations: RotateSubcommand[], DeviceIndex?: number, Id?: number);
}
export declare class VectorSubcommand extends GenericMessageSubcommand {
    Position: number;
    Duration: number;
    constructor(Index: number, Position: number, Duration: number);
}
export declare class LinearCmd extends ButtplugDeviceMessage {
    Vectors: VectorSubcommand[];
    DeviceIndex: number;
    Id: number;
    static Name: string;
    static Create(deviceIndex: number, commands: [number, number][]): LinearCmd;
    constructor(Vectors: VectorSubcommand[], DeviceIndex?: number, Id?: number);
}
export declare class SensorReadCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    SensorIndex: number;
    SensorType: SensorType;
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, SensorIndex: number, SensorType: SensorType, Id?: number);
}
export declare class SensorReading extends ButtplugDeviceMessage {
    DeviceIndex: number;
    SensorIndex: number;
    SensorType: SensorType;
    Data: number[];
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, SensorIndex: number, SensorType: SensorType, Data: number[], Id?: number);
}
export declare class RawReadCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Endpoint: string;
    ExpectedLength: number;
    Timeout: number;
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, Endpoint: string, ExpectedLength: number, Timeout: number, Id?: number);
}
export declare class RawWriteCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Endpoint: string;
    Data: Uint8Array;
    WriteWithResponse: boolean;
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, Endpoint: string, Data: Uint8Array, WriteWithResponse: boolean, Id?: number);
}
export declare class RawSubscribeCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Endpoint: string;
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, Endpoint: string, Id?: number);
}
export declare class RawUnsubscribeCmd extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Endpoint: string;
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, Endpoint: string, Id?: number);
}
export declare class RawReading extends ButtplugDeviceMessage {
    DeviceIndex: number;
    Endpoint: string;
    Data: number[];
    Id: number;
    static Name: string;
    constructor(DeviceIndex: number, Endpoint: string, Data: number[], Id?: number);
}
