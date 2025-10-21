"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const Messages = __importStar(require("../src/core/Messages"));
const MessageUtils_1 = require("../src/core/MessageUtils");
const utils_1 = require("./utils");
(0, utils_1.SetupTestSuite)();
describe("Message", () => {
    it("Converts ok message to json correctly", () => {
        const ok = new Messages.Ok(2);
        expect(ok.toJSON()).toEqual('{"Ok":{"Id":2}}');
    });
    it("Converts ok message from json correctly", () => {
        const jsonStr = '[{"Ok":{"Id":2}}]';
        expect((0, MessageUtils_1.fromJSON)(jsonStr)).toEqual([new Messages.Ok(2)]);
    });
    it("Converts DeviceList message from json correctly", () => {
        // tslint:disable-next-line:max-line-length
        const jsonStr = `
       [
        {
          "DeviceList": {
            "Id": 1,
            "Devices": [
              {
                "DeviceName": "Test Vibrator",
                "DeviceIndex": 0,
                "DeviceMessages": {
                  "ScalarCmd": [
                    {
                      "StepCount": 20,
                      "FeatureDescriptor": "Clitoral Stimulator",
                      "ActuatorType": "Vibrate"
                    },
                    {
                      "StepCount": 20,
                      "FeatureDescriptor": "Insertable Vibrator",
                      "ActuatorType": "Vibrate"
                    }
                  ],
                  "StopDeviceCmd": {}
                }
              },
              {
                "DeviceName": "Test Stroker",
                "DeviceIndex": 1,
                "DeviceMessageTimingGap": 100,
                "DeviceDisplayName": "User set name",
                "DeviceMessages": {
                  "LinearCmd": [ {
                    "StepCount": 100,
                    "ActuatorType": "Position",
                    "FeatureDescriptor": "Stroker"
                  } ],
                  "StopDeviceCmd": {}
                }
              }
            ]
          }
        }
      ]       
       `;
        expect((0, MessageUtils_1.fromJSON)(jsonStr))
            .toEqual([
            new Messages.DeviceList([
                new Messages.DeviceInfo({
                    DeviceIndex: 0,
                    DeviceName: "Test Vibrator",
                    DeviceMessages: new Messages.MessageAttributes({
                        ScalarCmd: [
                            new Messages.GenericDeviceMessageAttributes({ FeatureDescriptor: "Clitoral Stimulator", ActuatorType: Messages.ActuatorType.Vibrate, StepCount: 20, Index: 0 }),
                            new Messages.GenericDeviceMessageAttributes({ FeatureDescriptor: "Insertable Vibrator", ActuatorType: Messages.ActuatorType.Vibrate, StepCount: 20, Index: 1 }),
                        ],
                        StopDeviceCmd: {}
                    })
                }),
                new Messages.DeviceInfo({
                    DeviceIndex: 1,
                    DeviceName: "Test Stroker",
                    DeviceMessages: new Messages.MessageAttributes({
                        LinearCmd: [new Messages.GenericDeviceMessageAttributes({ FeatureDescriptor: "Stroker", ActuatorType: Messages.ActuatorType.Position, StepCount: 100 })],
                        StopDeviceCmd: {}
                    }), DeviceDisplayName: "User set name", DeviceMessageTimingGap: 100
                })
            ], 1)
        ]);
    });
    it("Converts DeviceAdded message from json correctly", () => {
        const jsonStr = `
       [
        {
          "DeviceAdded": {
            "Id": 0,
            "DeviceName": "Test Vibrator",
            "DeviceIndex": 0,
            "DeviceMessageTimingGap": 100,
            "DeviceDisplayName": "Rabbit Vibrator",
            "DeviceMessages": {
              "ScalarCmd": [
                {
                  "StepCount": 20,
                  "FeatureDescriptor": "Clitoral Stimulator",
                  "ActuatorType": "Vibrate"
                },
                {
                  "StepCount": 20,
                  "FeatureDescriptor": "Insertable Vibrator",
                  "ActuatorType": "Vibrate"
                }
              ],
              "StopDeviceCmd": {}
             }
          }
        }
      ]`;
        expect((0, MessageUtils_1.fromJSON)(jsonStr)[0])
            .toEqual(new Messages.DeviceAdded({
            DeviceIndex: 0,
            DeviceName: "Test Vibrator",
            DeviceMessages: new Messages.MessageAttributes({
                ScalarCmd: [
                    new Messages.GenericDeviceMessageAttributes({ FeatureDescriptor: "Clitoral Stimulator", ActuatorType: Messages.ActuatorType.Vibrate, StepCount: 20 }),
                    new Messages.GenericDeviceMessageAttributes({ FeatureDescriptor: "Insertable Vibrator", ActuatorType: Messages.ActuatorType.Vibrate, StepCount: 20, Index: 1 })
                ],
                StopDeviceCmd: {}
            }), DeviceDisplayName: "Rabbit Vibrator", DeviceMessageTimingGap: 100
        }));
    });
    it("Converts Error message from json correctly", () => {
        const jsonStr = '[{"Error":{"Id":2,"ErrorCode":3,"ErrorMessage":"TestError"}}]';
        expect((0, MessageUtils_1.fromJSON)(jsonStr)).toEqual([new Messages.Error("TestError", Messages.ErrorClass.ERROR_MSG, 2)]);
    });
    /*
 it("Handles Device Commands with Subcommand arrays correctly",
    () => {
      const jsonStr = '[{"VibrateCmd":{"Id":2, "DeviceIndex": 3, "Speeds": [{ "Index": 0, "Speed": 1.0}, {"Index": 1, "Speed": 0.5}]}}]';
      expect(fromJSON(jsonStr)).toEqual([new Messages.VibrateCmd([{Index: 0, Speed: 1.0}, {Index: 1, Speed: 0.5}], 3, 2)]);
    });
    */
});
//# sourceMappingURL=test-messages.js.map