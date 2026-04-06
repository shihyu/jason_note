"""
Binance 永續合約 K線數據下載器
"""

import asyncio
import aiohttp
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

BINANCE_URL = "https://fapi.binance.com"
DOWNLOAD_DIR = Path("data/raw")
REQUEST_DELAY = 0.2
CONCURRENT = 15

COLS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trades",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]


async def download_symbol(session, sym, start, end, sem, progress, lock):
    async with sem:
        all_data = []
        cur = start

        while cur < end:
            params = {"symbol": sym, "interval": "1m", "limit": 1000, "startTime": cur}
            for retry in range(5):
                try:
                    async with session.get(
                        f"{BINANCE_URL}/fapi/v1/klines", params=params
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if not data:
                                break
                            all_data.extend(data)
                            cur = int(data[-1][6]) + 1
                            if len(data) < 1000:
                                cur = end
                            break
                        elif resp.status == 429:
                            await asyncio.sleep(3 * (retry + 1))
                            continue
                        else:
                            break
                except Exception as e:
                    await asyncio.sleep(2)
                    continue

            await asyncio.sleep(REQUEST_DELAY)

        if all_data:
            df = pd.DataFrame(all_data, columns=COLS)
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            for c in ["open", "high", "low", "close", "volume", "quote_volume"]:
                df[c] = df[c].astype(float)
            cols = [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "quote_volume",
            ]
            df[cols].to_parquet(DOWNLOAD_DIR / f"{sym}.parquet")

        async with lock:
            progress[0] += 1
            p = progress[0]
            total = progress[1]
            if p % 10 == 0 or p == total:
                print(f"  [{p}/{total}] {sym}: {len(all_data)} rows")


async def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    with open("symbols.txt") as f:
        symbols = [s.strip() for s in f if s.strip()]

    start = int(datetime(2025, 1, 1).timestamp() * 1000)
    end = int(datetime.now().timestamp() * 1000)

    print(f"下載 {len(symbols)} 幣種 (2025-01-01 ~ now)")
    print(f"併發: {CONCURRENT}, 間隔: {REQUEST_DELAY}s")
    print()

    sem = asyncio.Semaphore(CONCURRENT)
    progress = [0, symbols]
    lock = asyncio.Lock()

    conn = aiohttp.TCPConnector(limit=CONCURRENT * 2)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [
            download_symbol(session, sym, start, end, sem, progress, lock)
            for sym in symbols
        ]
        await asyncio.gather(*tasks)

    files = len(list(DOWNLOAD_DIR.glob("*.parquet")))
    print(f"\n完成! {files}/{len(symbols)} 檔案")
    print(
        f"磁盤: {sum(f.stat().st_size for f in DOWNLOAD_DIR.glob('*.parquet')) / 1024 / 1024:.1f} MB"
    )


if __name__ == "__main__":
    asyncio.run(main())
