import { EventEmitter } from 'eventemitter3';

export declare enum ButtplugLogLevel {
    Off = 0,
    Error = 1,
    Warn = 2,
    Info = 3,
    Debug = 4,
    Trace = 5
}
/**
 * Representation of log messages for the internal logging utility.
 */
export declare class LogMessage {
    /** Timestamp for the log message */
    private timestamp;
    /** Log Message */
    private logMessage;
    /** Log Level */
    private logLevel;
    /**
     * @param logMessage Log message.
     * @param logLevel: Log severity level.
     */
    constructor(logMessage: string, logLevel: ButtplugLogLevel);
    /**
     * Returns the log message.
     */
    get Message(): string;
    /**
     * Returns the log message level.
     */
    get LogLevel(): ButtplugLogLevel;
    /**
     * Returns the log message timestamp.
     */
    get Timestamp(): string;
    /**
     * Returns a formatted string with timestamp, level, and message.
     */
    get FormattedMessage(): string;
}
/**
 * Simple, global logging utility for the Buttplug client and server. Keeps an
 * internal static reference to an instance of itself (singleton pattern,
 * basically), and allows message logging throughout the module.
 */
export declare class ButtplugLogger extends EventEmitter {
    /** Singleton instance for the logger */
    protected static sLogger: ButtplugLogger | undefined;
    /** Sets maximum log level to log to console */
    protected maximumConsoleLogLevel: ButtplugLogLevel;
    /** Sets maximum log level for all log messages */
    protected maximumEventLogLevel: ButtplugLogLevel;
    /**
     * Returns the stored static instance of the logger, creating one if it
     * doesn't currently exist.
     */
    static get Logger(): ButtplugLogger;
    /**
     * Constructor. Can only be called internally since we regulate ButtplugLogger
     * ownership.
     */
    protected constructor();
    /**
     * Set the maximum log level to output to console.
     */
    get MaximumConsoleLogLevel(): ButtplugLogLevel;
    /**
     * Get the maximum log level to output to console.
     */
    set MaximumConsoleLogLevel(buttplugLogLevel: ButtplugLogLevel);
    /**
     * Set the global maximum log level
     */
    get MaximumEventLogLevel(): ButtplugLogLevel;
    /**
     * Get the global maximum log level
     */
    set MaximumEventLogLevel(logLevel: ButtplugLogLevel);
    /**
     * Log new message at Error level.
     */
    Error(msg: string): void;
    /**
     * Log new message at Warn level.
     */
    Warn(msg: string): void;
    /**
     * Log new message at Info level.
     */
    Info(msg: string): void;
    /**
     * Log new message at Debug level.
     */
    Debug(msg: string): void;
    /**
     * Log new message at Trace level.
     */
    Trace(msg: string): void;
    /**
     * Checks to see if message should be logged, and if so, adds message to the
     * log buffer. May also print message and emit event.
     */
    protected AddLogMessage(msg: string, level: ButtplugLogLevel): void;
}
