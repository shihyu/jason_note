import asyncio
import argparse
import json
import time
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

import websockets
import requests


BINANCE_WS_URL = "wss://stream.binance.com:9443/stream"
BATCH_SIZE = 50
INTERVAL_SEC = 59


@dataclass
class TickBucket:
    high: float = field(default_factory=lambda: float("-inf"))
    low: float = field(default_factory=lambda: float("inf"))
    open: float | None = None
    close: float | None = None
    volume: float = 0.0


def get_usdt_symbols():
    resp = requests.get("https://api.binance.com/api/v3/exchangeInfo", timeout=10)
    data = resp.json()
    return [
        s["symbol"]
        for s in data.get("symbols", [])
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
    ]


async def stream_trades(
    symbols: list[str], buckets: dict, hourly_vol: dict, running: dict
):
    streams = [f"{s.lower()}@trade" for s in symbols]
    params = "/".join(streams)
    uri = f"{BINANCE_WS_URL}?streams={params}"

    async with websockets.connect(uri, ping_interval=30) as ws:
        while running["value"]:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            except asyncio.TimeoutError:
                await ws.ping()
                continue

            if "data" in msg:
                d = msg["data"]
                sym = d["s"]
                price = float(d["p"])
                qty = float(d["q"])
                ts = int(d["T"])
                minute_ts = ts // 60000 * 60000
                quote_vol = price * qty

                if minute_ts not in buckets[sym]:
                    buckets[sym][minute_ts] = TickBucket()
                b = buckets[sym][minute_ts]
                if b.open is None:
                    b.open = price
                b.high = max(b.high, price)
                b.low = min(b.low, price)
                b.close = price
                b.volume += quote_vol

                if sym not in hourly_vol:
                    hourly_vol[sym] = 0.0
                hourly_vol[sym] += quote_vol


def display_width(s: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in str(s)
    )


def pad(s: str, width: int) -> str:
    return s + " " * (width - display_width(s))


def format_volume(v: float) -> str:
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f}B"
    elif v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    elif v >= 1_000:
        return f"{v / 1_000:.2f}K"
    else:
        return f"{v:.2f}"


def to_markdown(
    buckets: dict,
    hourly_vol: dict,
    floatfmt: str = ".2f",
    tablefmt: str = "heavy_grid",
    top_n: int | None = None,
) -> str:
    now = int(time.time() * 1000)
    one_hour_ago = now - 3600 * 1000
    current_minute = now // 60000 * 60000

    results = []
    for sym, sym_buckets in buckets.items():
        vol_1h = sum(v.volume for ts, v in sym_buckets.items() if ts >= one_hour_ago)
        for minute_ts, v in sym_buckets.items():
            if minute_ts == current_minute and v.open is not None:
                if v.low > 0:
                    range_pct = (v.high - v.low) / v.low * 100
                else:
                    range_pct = 0.0
                dt = datetime.fromtimestamp(minute_ts / 1000).strftime("%H:%M")
                results.append(
                    (sym, dt, v.open, v.high, v.low, v.close, range_pct, vol_1h)
                )

    if not results:
        return "# No Data\n"

    results.sort(key=lambda x: x[7], reverse=True)
    if top_n is not None:
        results = results[:top_n]
    results.sort(key=lambda x: x[6], reverse=True)

    header = [
        "Symbol",
        "Minute",
        "Open",
        "High",
        "Low",
        "Close",
        "Ampl%",
        "Vol(USDT,1h)",
    ]
    col_widths = [
        max(display_width(str(r[i])) for r in results) for i in range(len(header))
    ]
    for i, h in enumerate(header):
        col_widths[i] = max(col_widths[i], display_width(h))

    sep_map = {"heavy_grid": "━", "grid": "-"}
    sep = sep_map.get(tablefmt, "-")
    vsep = "│"

    md = "# USDT Pairs - 1 Min Tick Amplitude\n\n"
    md += f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Pairs tracked:** {len(buckets)}\n\n"

    md += (
        vsep
        + "".join(f" {pad(h, col_widths[i])} {vsep}" for i, h in enumerate(header))
        + "\n"
    )
    md += (
        vsep
        + "".join(f" {sep * col_widths[i]} {vsep}" for i in range(len(header)))
        + "\n"
    )

    for r in results:
        row_vals = [
            r[0],
            r[1],
            f"{r[2]:{floatfmt}}",
            f"{r[3]:{floatfmt}}",
            f"{r[4]:{floatfmt}}",
            f"{r[5]:{floatfmt}}",
            f"{r[6]:{floatfmt}}",
            format_volume(r[7]),
        ]
        md += (
            vsep
            + "".join(
                f" {pad(str(v), col_widths[i])} {vsep}" for i, v in enumerate(row_vals)
            )
            + "\n"
        )

    return md


async def calculate_kline_range(top_n: int | None):
    symbols = get_usdt_symbols()
    print(f"Found {len(symbols)} USDT pairs")

    buckets: dict[str, dict[int, TickBucket]] = defaultdict(dict)
    hourly_vol: dict[str, float] = {}
    running = {"value": True}

    batches = [symbols[i : i + BATCH_SIZE] for i in range(0, len(symbols), BATCH_SIZE)]
    print(f"Connecting to {len(batches)} WebSocket streams...")

    tasks = [stream_trades(batch, buckets, hourly_vol, running) for batch in batches]

    async def reporter():
        for _ in range(12):
            await asyncio.sleep(INTERVAL_SEC)
            print(to_markdown(buckets, hourly_vol, top_n=top_n))
            now = int(time.time() * 1000)
            one_hour_ago = now - 3600 * 1000
            for sym in buckets:
                buckets[sym] = {
                    ts: v for ts, v in buckets[sym].items() if ts >= one_hour_ago
                }
            hourly_vol.clear()
        running["value"] = False

    tasks.append(reporter())
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="USDT Pairs 1 Min Tick Amplitude")
    parser.add_argument(
        "--top", type=int, default=None, help="Show top N pairs by 1h volume"
    )
    args = parser.parse_args()
    asyncio.run(calculate_kline_range(args.top))
