"use strict";
/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ButtplugLogger = exports.LogMessage = exports.ButtplugLogLevel = void 0;
const eventemitter3_1 = require("eventemitter3");
var ButtplugLogLevel;
(function (ButtplugLogLevel) {
    ButtplugLogLevel[ButtplugLogLevel["Off"] = 0] = "Off";
    ButtplugLogLevel[ButtplugLogLevel["Error"] = 1] = "Error";
    ButtplugLogLevel[ButtplugLogLevel["Warn"] = 2] = "Warn";
    ButtplugLogLevel[ButtplugLogLevel["Info"] = 3] = "Info";
    ButtplugLogLevel[ButtplugLogLevel["Debug"] = 4] = "Debug";
    ButtplugLogLevel[ButtplugLogLevel["Trace"] = 5] = "Trace";
})(ButtplugLogLevel || (exports.ButtplugLogLevel = ButtplugLogLevel = {}));
/**
 * Representation of log messages for the internal logging utility.
 */
class LogMessage {
    /**
     * @param logMessage Log message.
     * @param logLevel: Log severity level.
     */
    constructor(logMessage, logLevel) {
        const a = new Date();
        const hour = a.getHours();
        const min = a.getMinutes();
        const sec = a.getSeconds();
        this.timestamp = `${hour}:${min}:${sec}`;
        this.logMessage = logMessage;
        this.logLevel = logLevel;
    }
    /**
     * Returns the log message.
     */
    get Message() {
        return this.logMessage;
    }
    /**
     * Returns the log message level.
     */
    get LogLevel() {
        return this.logLevel;
    }
    /**
     * Returns the log message timestamp.
     */
    get Timestamp() {
        return this.timestamp;
    }
    /**
     * Returns a formatted string with timestamp, level, and message.
     */
    get FormattedMessage() {
        return `${ButtplugLogLevel[this.logLevel]} : ${this.timestamp} : ${this.logMessage}`;
    }
}
exports.LogMessage = LogMessage;
/**
 * Simple, global logging utility for the Buttplug client and server. Keeps an
 * internal static reference to an instance of itself (singleton pattern,
 * basically), and allows message logging throughout the module.
 */
class ButtplugLogger extends eventemitter3_1.EventEmitter {
    /**
     * Returns the stored static instance of the logger, creating one if it
     * doesn't currently exist.
     */
    static get Logger() {
        if (ButtplugLogger.sLogger === undefined) {
            ButtplugLogger.sLogger = new ButtplugLogger();
        }
        return this.sLogger;
    }
    /**
     * Constructor. Can only be called internally since we regulate ButtplugLogger
     * ownership.
     */
    constructor() {
        super();
        /** Sets maximum log level to log to console */
        this.maximumConsoleLogLevel = ButtplugLogLevel.Off;
        /** Sets maximum log level for all log messages */
        this.maximumEventLogLevel = ButtplugLogLevel.Off;
    }
    /**
     * Set the maximum log level to output to console.
     */
    get MaximumConsoleLogLevel() {
        return this.maximumConsoleLogLevel;
    }
    /**
     * Get the maximum log level to output to console.
     */
    set MaximumConsoleLogLevel(buttplugLogLevel) {
        this.maximumConsoleLogLevel = buttplugLogLevel;
    }
    /**
     * Set the global maximum log level
     */
    get MaximumEventLogLevel() {
        return this.maximumEventLogLevel;
    }
    /**
     * Get the global maximum log level
     */
    set MaximumEventLogLevel(logLevel) {
        this.maximumEventLogLevel = logLevel;
    }
    /**
     * Log new message at Error level.
     */
    Error(msg) {
        this.AddLogMessage(msg, ButtplugLogLevel.Error);
    }
    /**
     * Log new message at Warn level.
     */
    Warn(msg) {
        this.AddLogMessage(msg, ButtplugLogLevel.Warn);
    }
    /**
     * Log new message at Info level.
     */
    Info(msg) {
        this.AddLogMessage(msg, ButtplugLogLevel.Info);
    }
    /**
     * Log new message at Debug level.
     */
    Debug(msg) {
        this.AddLogMessage(msg, ButtplugLogLevel.Debug);
    }
    /**
     * Log new message at Trace level.
     */
    Trace(msg) {
        this.AddLogMessage(msg, ButtplugLogLevel.Trace);
    }
    /**
     * Checks to see if message should be logged, and if so, adds message to the
     * log buffer. May also print message and emit event.
     */
    AddLogMessage(msg, level) {
        // If nothing wants the log message we have, ignore it.
        if (level > this.maximumEventLogLevel &&
            level > this.maximumConsoleLogLevel) {
            return;
        }
        const logMsg = new LogMessage(msg, level);
        // Clients and console logging may have different needs. For instance, it
        // could be that the client requests trace level, while all we want in the
        // console is info level. This makes sure the client can't also spam the
        // console.
        if (level <= this.maximumConsoleLogLevel) {
            console.log(logMsg.FormattedMessage);
        }
        if (level <= this.maximumEventLogLevel) {
            this.emit('log', logMsg);
        }
    }
}
exports.ButtplugLogger = ButtplugLogger;
/** Singleton instance for the logger */
ButtplugLogger.sLogger = undefined;
//# sourceMappingURL=Logging.js.map