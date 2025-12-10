


export interface BatchUpdateBalancesRequest {
    account_id: number;
    user_id: number;
    shard_id: number;
    balance_changes: BalanceChange[];
}

export interface BalanceChange {
    currency_code: string;
    available_delta: number;
    frozen_delta: number;
}
