import { v4 as uuidv4 } from 'uuid';
import { getRandomFloat, getRandomInt } from '../module/utils';

export function newRandomBalanceChange(minAmount: number, maxAmount: number): BalanceChange {
    let val = getRandomFloat(minAmount, maxAmount, 8);
    let frozeVal = val < 0 ? -val : 0;

    let currencies = ['USDC', 'BTC', 'ETH', 'SOL', 'USDT', "BNB"];
    let randomIndex = Math.floor(Math.random() * currencies.length);
    let currency = currencies[randomIndex];

    return newBalanceChange(currency, currency, val.toString(), frozeVal.toString());
}

export function newRandBalanceChangeEvent(maxUID: number, maxChanges: number, minAmount: number, maxAmount: number): SubmitBalanceChangeRequest {
    let uid = getRandomInt(1, maxUID);
    let numChanges = getRandomInt(1, maxChanges);
    let changes: BalanceChange[] = [];
    for (let i = 0; i < numChanges; i++) {
        changes.push(newRandomBalanceChange(-10000, 10000));
    }
    return newDepositBalanceChangeEvent(uid.toString(), uid.toString(), changes);
}


export function newOrderBalanceChangeEvent(accountId: string, userId: string, orderId: string, balanceChanges: BalanceChange[]): SubmitBalanceChangeRequest {
    return {
        eventId: uuidv4(),
        eventType: 'OrderCreated',
        eventTypeId: '1',
        accountId: accountId,
        userId: userId,
        sourceService: 'order-svc',
        sourceSvcId: '1',
        relatedOrderId: Math.floor(Math.random() * 999999 + 1).toString(),
        idempotencyKey: uuidv4(),
        createdMsec: Date.now().toString(),
        changes: balanceChanges,
    } as SubmitBalanceChangeRequest;
}

export function newDepositBalanceChangeEvent(accountId: string, userId: string, balanceChanges: BalanceChange[]): SubmitBalanceChangeRequest {
    return {
        eventId: uuidv4(),
        eventType: 'DepositCreated',
        eventTypeId: '2',
        accountId: accountId,
        userId: userId,
        sourceService: 'wallet-svc',
        sourceSvcId: '2',
        relatedOrderId: Math.floor(Math.random() * 999999 + 1).toString(),
        idempotencyKey: uuidv4(),
        createdMsec: Date.now().toString(), // Convert to microseconds
        changes: balanceChanges,
    } as SubmitBalanceChangeRequest;
}


export function newWithdrawBalanceChangeEvent(accountId: string, userId: string, balanceChanges: BalanceChange[]): SubmitBalanceChangeRequest {
    return {
        eventId: uuidv4(),
        eventType: 'WithdrawCreated',
        eventTypeId: '3',
        accountId: accountId,
        userId: userId,
        sourceService: 'wallet-svc',
        sourceSvcId: '2',
        relatedOrderId: Math.floor(Math.random() * 999999 + 1).toString(),
        idempotencyKey: uuidv4(),
        createdMsec: Date.now().toString(),
        changes: balanceChanges,
    } as SubmitBalanceChangeRequest;
}

export function newBalanceChange(currencyCode: string, currencySymbol: string, availableDelta: string, frozenDelta: string, fallbackCurrencyCode?: string, fallbackCurrencySymbol?: string, fallbackAvailableDelta?: string, fallbackFrozenDelta?: string): BalanceChange {
    return {
        changeId: Math.floor(Math.random() * 999999 + 1).toString(),
        currencyCode: currencyCode,
        currencySymbol: currencySymbol,
        availableDelta: availableDelta,
        frozenDelta: frozenDelta,
        fallbackCurrencyCode: fallbackCurrencyCode,
        fallbackCurrencySymbol: fallbackCurrencySymbol,
        fallbackAvailableDelta: fallbackAvailableDelta,
        fallbackFrozenDelta: fallbackFrozenDelta,
    } as BalanceChange;
}

export function newBatchSubmitBalanceChangesRequestJSONPayload(requests: SubmitBalanceChangeRequest[]): string {
    const batchRequest: BatchSubmitBalanceChangesRequest = {
        requests: requests,
    };
    return JSON.stringify(batchRequest);
}

/**
 * 批次提交餘額變動的請求
 */
export interface BatchSubmitBalanceChangesRequest {
    /** 包含多個 SubmitBalanceChangeRequest 的列表 */
    requests: SubmitBalanceChangeRequest[];
}

// --------------------------------------------------------

/**
 * 用於提交餘額變動的單一請求 (通常代表一個事件)
 */
export interface SubmitBalanceChangeRequest {
    /** 事件的唯一 ID */
    eventId: string;

    /** 事件類型名稱 (例如: "Deposit", "Withdrawal") */
    eventType: string;

    /** 事件類型的數字 ID */
    eventTypeId: string; // Go 中的 int64 推薦使用 string

    /** 帳戶 ID */
    accountId: string;

    /** 使用者 ID */
    userId: string;

    /** 來源服務名稱 (例如: "gateway", "order-svc") */
    sourceService: string;

    /** 來源服務的 ID */
    sourceSvcId: string;

    /** 相關訂單 ID */
    relatedOrderId: string;

    /** 冪等性鍵 (防止重複提交的唯一識別碼) */
    idempotencyKey: string;

    /** 創建時間 (毫秒級 Unix 時間戳) */
    createdMsec: string;

    /** 該事件涉及的所有餘額變動列表 */
    changes: BalanceChange[];
}



/**
 * 定義單個餘額變動的詳細資訊
 */
export interface BalanceChange {
    /** 變動的唯一 ID */
    changeId: string; // Go 中的 int64 在 JS 中通常表示為 string 或 number，但對於 ID 推薦 string

    /** 主要貨幣代碼 (例如: "USD", "TWD") */
    currencyCode: string;

    /** 主要貨幣符號 (例如: "$", "NT$") */
    currencySymbol: string;

    /** 可用餘額的變化量 (正數為增加, 負數為減少) */
    availableDelta: string;

    /** 凍結餘額的變化量 (正數為增加, 負數為減少) */
    frozenDelta: string;

    /** 備用/後備貨幣代碼 (Fallback Currency Code) */
    fallbackCurrencyCode?: string;

    /** 備用/後備貨幣符號 */
    fallbackCurrencySymbol?: string;

    /** 備用貨幣可用餘額的變化量 */
    fallbackAvailableDelta?: string;

    /** 備用貨幣凍結餘額的變化量 */
    fallbackFrozenDelta?: string;
}
