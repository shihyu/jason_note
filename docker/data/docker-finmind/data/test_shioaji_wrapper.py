from Jlab.watcher import Watcher
from Jlab.shioaji_wrapper import ShioajiWrapper
import shioaji as sj
import json
import os
import sys


def login(simulation=False):
    api = sj.Shioaji(simulation=simulation)
    token_file = os.environ["HOME"] + "/.mybin/shioaji_tokens.json"
    with open(token_file, "r") as f:
        users = json.load(f)
        print("All users: " + ", ".join(users.keys()))

        user = input("Select a user from the list above: ")
        if user not in users:
            print("User not found.")
            sys.exit()

        api.login(
            users[user]["api_key"], users[user]["secret_key"], fetch_contract=False
        )
        api.fetch_contracts(contract_download=True)
        print(f"Logged in as {user}")
        return api


def simulation(api):
    contract = api.Contracts.Stocks.TSE["2890"]
    # order - edit it
    order = api.Order(
        action=sj.constant.Action.Buy,
        price=20,
        quantity=1,
        price_type=sj.constant.StockPriceType.LMT,
        order_type=sj.constant.OrderType.ROD,
        account=api.stock_account,
    )

    # place order
    trade = api.place_order(contract, order, timeout=0)
    print(trade)


if __name__ == "__main__":
    Watcher()
    # 設置參數以決定是使用模擬還是實際交易
    SIMULATION = False
    api = login(simulation=SIMULATION)
    if SIMULATION:
        simulation(api)
    else:
        shioaji_wrapper = ShioajiWrapper(api)
        contract = shioaji_wrapper.get_near_month_txf_contract()
        print(contract)
        # print(api.account_balance())
        # print(api.list_positions(api.stock_account))
        contracts = [api.Contracts.Stocks["2330"], api.Contracts.Stocks["2317"]]
        snapshots = api.snapshots(contracts)
        print(snapshots)
        # Stock default account  證券目前的預設帳戶
        print(api.stock_account)

        # Futures default account 期貨目前的預設帳戶
        print(api.futopt_account)
        print(shioaji_wrapper.get_stock_list())
        print(shioaji_wrapper.is_market_open())
        print(shioaji_wrapper.get_latest_option_contract())

    api.logout()
