"""
配對交易策略核心

進場邏輯：
- 每分鐘結束後計算所有幣種振幅
- Long 振幅第1名
- Short 振幅第3, 4, 5名

出场邏輯：
- 振幅收縮到 entry_amp / 3 以下 → 平倉
- 振幅擴大到 entry_amp * 2 → 止損
- 超過 max_hold 分鐘 → 強制平倉
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple


@dataclass
class Trade:
    symbol: str
    side: str  # "long" or "short"
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl_pct: float = 0.0
    reason: str = ""  # "exit_amp", "stop_loss", "max_hold"


@dataclass
class Position:
    symbol: str
    side: str
    entry_time: datetime
    entry_price: float
    entry_amp: float
    bar_count: int = 0


@dataclass
class StrategyParams:
    entry_amp: float = 0.005  # 進場振幅閾值 (0.5%)
    top_n: int = 5  # 取前N名
    exit_amp_ratio: float = 0.33  # 出場 = entry_amp * ratio
    stop_loss_ratio: float = 2.0  # 止損 = entry_amp * ratio
    max_hold: int = 5  # 最大持有分鐘數


class PairsTradingStrategy:
    def __init__(self, params: Optional[StrategyParams] = None):
        self.params = params or StrategyParams()
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []

    def calculate_amplitude(self, df: pd.DataFrame) -> pd.Series:
        """計算每分鐘振幅"""
        return (df["high"] - df["low"]) / df["low"]

    def rank_by_amplitude(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算振幅並排名"""
        amp = self.calculate_amplitude(df)
        ranked = df.copy()
        ranked["amplitude"] = amp
        ranked["rank"] = ranked.groupby("open_time")["amplitude"].rank(ascending=False)
        return ranked.sort_values(["open_time", "rank"])

    def select_pairs(
        self, ranked_df: pd.DataFrame, timestamp: datetime
    ) -> Tuple[List, List]:
        """選擇配對：Long #1, Short #3, #4, #5"""
        current = ranked_df[ranked_df["open_time"] == timestamp]

        longs = []
        shorts = []

        if len(current) >= 3:
            sorted_df = current.sort_values(by="rank").head(self.params.top_n)

            if len(sorted_df) >= 1:
                longs.append(sorted_df.iloc[0].to_dict())

            if len(sorted_df) >= 5:
                shorts.extend(sorted_df.iloc[2:5].to_dict("records"))
            elif len(sorted_df) >= 3:
                shorts.extend(sorted_df.iloc[2:].to_dict("records"))

        return longs, shorts

    def check_exit(self, row: pd.Series, pos: Position) -> Tuple[bool, str]:
        """檢查是否需要平倉"""
        current_amp = row["amplitude"]

        # 振幅收縮到 exit_amp 以下 → 平倉
        exit_amp = self.params.entry_amp * self.params.exit_amp_ratio
        if current_amp < exit_amp:
            return True, "exit_amp"

        # 振幅擴大到 stop_loss → 止損
        stop_amp = self.params.entry_amp * self.params.stop_loss_ratio
        if current_amp > stop_amp:
            return True, "stop_loss"

        # 超過最大持有時間
        if pos.bar_count >= self.params.max_hold:
            return True, "max_hold"

        return False, ""

    def process_bar(self, ranked_df: pd.DataFrame, timestamp: datetime) -> List[Trade]:
        """處理單根K線"""
        new_trades = []

        current = ranked_df[ranked_df["open_time"] == timestamp]
        if current.empty:
            return new_trades

        amp_series = current.set_index("symbol")["amplitude"]

        # 檢查現有倉位
        for symbol, pos in list(self.positions.items()):
            if symbol not in amp_series.index:
                continue

            row = current[current["symbol"] == symbol].iloc[0]
            should_exit, reason = self.check_exit(row, pos)

            if should_exit:
                exit_price = row["close"]
                if pos.side == "long":
                    pnl_pct = (exit_price - pos.entry_price) / pos.entry_price
                else:
                    pnl_pct = (pos.entry_price - exit_price) / pos.entry_price

                trade = Trade(
                    symbol=symbol,
                    side=pos.side,
                    entry_time=pos.entry_time,
                    entry_price=pos.entry_price,
                    exit_time=timestamp,
                    exit_price=exit_price,
                    pnl_pct=pnl_pct,
                    reason=reason,
                )
                new_trades.append(trade)
                del self.positions[symbol]

        # 更新持倉計數
        for symbol, pos in self.positions.items():
            pos.bar_count += 1

        # 過濾符合進場條件的幣種（振幅 > entry_amp）
        eligible = current[current["amplitude"] >= self.params.entry_amp]

        longs, shorts = self.select_pairs(ranked_df, timestamp)

        # 開多頭
        for row in longs:
            symbol = row["symbol"]
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side="long",
                    entry_time=timestamp,
                    entry_price=row["close"],
                    entry_amp=row["amplitude"],
                    bar_count=0,
                )

        # 開空頭（最多3個）
        for i, row in enumerate(shorts[:3]):
            symbol = row["symbol"]
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side="short",
                    entry_time=timestamp,
                    entry_price=row["close"],
                    entry_amp=row["amplitude"],
                    bar_count=0,
                )

        return new_trades

    def run(self, df: pd.DataFrame) -> List[Trade]:
        """執行策略"""
        ranked = self.rank_by_amplitude(df)
        timestamps = sorted(ranked["open_time"].unique())

        for ts in timestamps:
            trades = self.process_bar(ranked, ts)
            self.trades.extend(trades)

        # 平掉所有剩余倉位
        for symbol, pos in list(self.positions.items()):
            last_row = ranked[ranked["symbol"] == symbol].iloc[-1]
            exit_price = last_row["close"]

            if pos.side == "long":
                pnl_pct = (exit_price - pos.entry_price) / pos.entry_price
            else:
                pnl_pct = (pos.entry_price - exit_price) / pos.entry_price

            trade = Trade(
                symbol=symbol,
                side=pos.side,
                entry_time=pos.entry_time,
                entry_price=pos.entry_price,
                exit_time=last_row["open_time"],
                exit_price=exit_price,
                pnl_pct=pnl_pct,
                reason="end_of_data",
            )
            self.trades.append(trade)

        return self.trades
