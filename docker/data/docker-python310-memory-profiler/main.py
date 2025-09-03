from pip import _internal
from memory_profiler import profile
import datetime as dt
import requests
import time
import httpx
import gc


def cb_write_log_to_file(tmp_list):
    for tmp in tmp_list:
        print(tmp, end="")


@profile(cb_func=cb_write_log_to_file, precision=4)
def call():
    url = "https://api.bitopro.com/v3/provisioning/trading-pairs"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(response.status_code, dt.datetime.now())
        return data
    else:
        print("Request failed with status code:", response.status_code)
    response.close()
    gc.collect()


def main():
    while True:
        time.sleep(0.2)
        data = call()


if __name__ == "__main__":
    print("Hello Docker world!")
    _internal.main(["list"])
    main()
