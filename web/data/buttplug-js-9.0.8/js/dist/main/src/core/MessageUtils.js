/*!
 * Buttplug JS Source Code File - Visit https://buttplug.io for more info about
 * the project. Licensed under the BSD 3-Clause license. See LICENSE file in the
 * project root for full license information.
 *
 * @copyright Copyright (c) Nonpolynomial Labs LLC. All rights reserved.
 */
'use strict';
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
exports.getMessageClassFromMessage = getMessageClassFromMessage;
exports.fromJSON = fromJSON;
const class_transformer_1 = require("class-transformer");
const Messages = __importStar(require("./Messages"));
function getMessageClass(type) {
    for (const value of Object.values(Messages)) {
        if (typeof value === 'function' && 'Name' in value && value.Name === type) {
            return value;
        }
    }
    return null;
}
function getMessageClassFromMessage(msg) {
    // Making the bold assumption all message classes have the Name static. Should define a
    // requirement for this in the abstract class.
    return getMessageClass(Object.getPrototypeOf(msg).constructor.Name);
}
function fromJSON(str) {
    const msgarray = JSON.parse(str);
    const msgs = [];
    for (const x of Array.from(msgarray)) {
        const type = Object.getOwnPropertyNames(x)[0];
        const cls = getMessageClass(type);
        if (cls) {
            const msg = (0, class_transformer_1.plainToInstance)(cls, x[type]);
            msg.update();
            msgs.push(msg);
        }
    }
    return msgs;
}
//# sourceMappingURL=MessageUtils.js.map