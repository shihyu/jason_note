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
const Logging_1 = require("../src/core/Logging");
const utils_1 = require("./utils");
(0, utils_1.SetupTestSuite)();
describe("Logging Tests", () => {
    class TestLogger extends Logging_1.ButtplugLogger {
        static ResetLogger() {
            Logging_1.ButtplugLogger.sLogger = new Logging_1.ButtplugLogger();
        }
    }
    let logger = TestLogger.Logger;
    beforeEach(() => {
        TestLogger.ResetLogger();
        logger = TestLogger.Logger;
    });
    it("Should log nothing at start.", () => __awaiter(void 0, void 0, void 0, function* () {
        let res;
        let rej;
        const p = new Promise((rs, rj) => { res = rs; rej = rj; });
        logger.addListener("log", (msg) => {
            rej();
        });
        logger.Debug("test");
        logger.Error("test");
        logger.Warn("test");
        logger.Info("test");
        logger.Trace("test");
        res();
        return p;
    }));
    it("Should log everything on trace.", () => __awaiter(void 0, void 0, void 0, function* () {
        let res;
        let rej;
        let count = 0;
        const p = new Promise((rs, rj) => { res = rs; rej = rj; });
        logger.MaximumEventLogLevel = Logging_1.ButtplugLogLevel.Trace;
        logger.addListener("log", (msg) => {
            count++;
        });
        logger.Debug("test");
        logger.Error("test");
        logger.Warn("test");
        logger.Info("test");
        logger.Trace("test");
        if (count === 5) {
            return Promise.resolve();
        }
        return Promise.reject("Log event count incorrect!");
    }));
    it("Should deal with different log levels for console and events", () => __awaiter(void 0, void 0, void 0, function* () {
        jest.spyOn(global.console, "log");
        let res;
        let rej;
        const p = new Promise((rs, rj) => { res = rs; rej = rj; });
        logger.addListener("log", (msg) => {
            rej();
        });
        logger.MaximumEventLogLevel = Logging_1.ButtplugLogLevel.Debug;
        logger.MaximumConsoleLogLevel = Logging_1.ButtplugLogLevel.Trace;
        logger.Trace("test");
        expect(console.log).toBeCalled();
        res();
        return p;
    }));
});
//# sourceMappingURL=test-logging.js.map