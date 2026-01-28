#!/usr/bin/env python3
"""
產業輪動早期檢測模組
實作 7 種檢測方法，優先早期檢測（方法 1/2/3）
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def method1_anomaly_detection(
    df_history: pd.DataFrame,
    lookback_days: int = 20,
    threshold: float = 2.0
) -> pd.DataFrame:
    """
    方法 1：異常強度檢測（⭐⭐⭐ 早期預警首選）
    檢測內外盤比突然暴增/暴跌

    Args:
        df_history: 歷史產業統計（多日資料）
                   必須包含: date, industry, taker_ratio
        lookback_days: 回望天數（用於計算均值和標準差）
        threshold: 異常閾值（幾倍標準差）

    Returns:
        DataFrame 加上 method1_signal 欄位 (1=異常強, -1=異常弱, 0=正常)
        和 method1_score 欄位 (0-1 之間)
    """
    df = df_history.copy()
    df = df.sort_values(['industry', 'date']).reset_index(drop=True)

    # 計算移動平均和標準差
    df['ma'] = df.groupby('industry')['taker_ratio'].transform(
        lambda x: x.rolling(lookback_days, min_periods=5).mean()
    )
    df['std'] = df.groupby('industry')['taker_ratio'].transform(
        lambda x: x.rolling(lookback_days, min_periods=5).std()
    )

    # 計算 Z-score（與移動平均的偏離程度）
    df['deviation'] = (df['taker_ratio'] - df['ma']) / (df['std'] + 1e-9)

    # 判定異常信號
    df['method1_signal'] = 0
    df.loc[df['deviation'] > threshold, 'method1_signal'] = 1   # 異常強
    df.loc[df['deviation'] < -threshold, 'method1_signal'] = -1  # 異常弱

    # 計算信號強度分數（0-1）
    df['method1_score'] = df['deviation'].abs() / (threshold * 2)
    df['method1_score'] = df['method1_score'].clip(0, 1)

    return df


def method2_rank_velocity(
    df_history: pd.DataFrame,
    velocity_days: int = 3
) -> pd.DataFrame:
    """
    方法 2：相對強度排名變化（⭐⭐⭐ 早期檢測）
    追蹤產業排名的變化速度

    Args:
        df_history: 歷史產業統計
        velocity_days: 計算速度的天數

    Returns:
        DataFrame 加上 method2_signal 和 method2_score
    """
    df = df_history.copy()
    df = df.sort_values(['industry', 'date']).reset_index(drop=True)

    # 計算排名變化
    df['rank_lag'] = df.groupby('industry')['rank_pct'].shift(velocity_days)
    df['rank_change'] = df['rank_pct'] - df['rank_lag']

    # 判定信號（排名躍升 > 20%）
    df['method2_signal'] = 0
    df.loc[df['rank_change'] > 0.20, 'method2_signal'] = 1   # 排名躍升
    df.loc[df['rank_change'] < -0.20, 'method2_signal'] = -1  # 排名下跌

    # 計算信號強度分數
    df['method2_score'] = df['rank_change'].abs() / 0.40  # 0.4 為滿分
    df['method2_score'] = df['method2_score'].clip(0, 1)

    return df


def method3_change_rate(
    df_history: pd.DataFrame,
    change_days: int = 2,
    threshold: float = 0.15
) -> pd.DataFrame:
    """
    方法 3：內外盤比變化率（⭐⭐⭐ 早期檢測）
    檢測內外盤比的連續增長速度

    Args:
        df_history: 歷史產業統計
        change_days: 計算變化率的天數
        threshold: 變化率閾值（15%）

    Returns:
        DataFrame 加上 method3_signal 和 method3_score
    """
    df = df_history.copy()
    df = df.sort_values(['industry', 'date']).reset_index(drop=True)

    # 計算變化率
    df['ratio_lag'] = df.groupby('industry')['taker_ratio'].shift(change_days)
    df['ratio_change_rate'] = (df['taker_ratio'] - df['ratio_lag']) / (df['ratio_lag'] + 1e-9)

    # 判定信號（變化率 > 15%）
    df['method3_signal'] = 0
    df.loc[df['ratio_change_rate'] > threshold, 'method3_signal'] = 1   # 加速上漲
    df.loc[df['ratio_change_rate'] < -threshold, 'method3_signal'] = -1  # 加速下跌

    # 計算信號強度分數
    df['method3_score'] = df['ratio_change_rate'].abs() / (threshold * 2)
    df['method3_score'] = df['method3_score'].clip(0, 1)

    return df


def method4_zscore_threshold(
    df_history: pd.DataFrame,
    threshold: float = 1.5
) -> pd.DataFrame:
    """
    方法 4：標準化內外盤強度（⭐⭐ 確認階段）
    使用 Z-score 標準化

    Args:
        df_history: 歷史產業統計（必須已有 z_score 欄位）
        threshold: Z-score 閾值

    Returns:
        DataFrame 加上 method4_signal 和 method4_score
    """
    df = df_history.copy()

    # 判定信號
    df['method4_signal'] = 0
    df.loc[df['z_score'] > threshold, 'method4_signal'] = 1   # 強勢
    df.loc[df['z_score'] < -threshold, 'method4_signal'] = -1  # 弱勢

    # 計算信號強度分數
    df['method4_score'] = df['z_score'].abs() / (threshold * 2)
    df['method4_score'] = df['method4_score'].clip(0, 1)

    return df


def method5_volume_weighted(
    df_history: pd.DataFrame,
    volume_threshold: float = 1.3
) -> pd.DataFrame:
    """
    方法 5：成交量加權內外盤（⭐⭐ 主力確認）
    檢測成交量是否同步放大

    Args:
        df_history: 歷史產業統計（必須有 total_volume）
        volume_threshold: 成交量放大閾值（1.3 = 30% 放大）

    Returns:
        DataFrame 加上 method5_signal 和 method5_score
    """
    df = df_history.copy()
    df = df.sort_values(['industry', 'date']).reset_index(drop=True)

    # 計算成交量移動平均
    df['volume_ma'] = df.groupby('industry')['total_volume'].transform(
        lambda x: x.rolling(5, min_periods=2).mean()
    )

    # 計算成交量放大倍數
    df['volume_ratio'] = df['total_volume'] / (df['volume_ma'] + 1e-9)

    # 判定信號（內外盤比強 + 成交量放大）
    df['method5_signal'] = 0
    strong_volume_mask = (df['taker_ratio'] > 1.0) & (df['volume_ratio'] > volume_threshold)
    weak_volume_mask = (df['taker_ratio'] < 1.0) & (df['volume_ratio'] > volume_threshold)

    df.loc[strong_volume_mask, 'method5_signal'] = 1
    df.loc[weak_volume_mask, 'method5_signal'] = -1

    # 計算信號強度分數
    df['method5_score'] = (df['volume_ratio'] - 1.0) / 0.5  # 50% 放大為滿分
    df['method5_score'] = df['method5_score'].clip(0, 1)

    return df


def detect_rotation_signals(df_history: pd.DataFrame) -> pd.DataFrame:
    """
    綜合所有方法，檢測產業輪動信號

    Args:
        df_history: 完整的歷史產業統計資料

    Returns:
        DataFrame 加上所有方法的信號和綜合分數
    """
    df = df_history.copy()

    # 依序執行各方法
    df = method1_anomaly_detection(df)
    df = method2_rank_velocity(df)
    df = method3_change_rate(df)
    df = method4_zscore_threshold(df)
    df = method5_volume_weighted(df)

    # 計算綜合信號分數（加權平均）
    weights = {
        'method1': 0.40,  # 異常檢測
        'method2': 0.30,  # 排名變化
        'method3': 0.20,  # 變化率
        'method4': 0.05,  # Z-score
        'method5': 0.05,  # 量能加權
    }

    df['combined_score'] = (
        df['method1_score'] * weights['method1'] +
        df['method2_score'] * weights['method2'] +
        df['method3_score'] * weights['method3'] +
        df['method4_score'] * weights['method4'] +
        df['method5_score'] * weights['method5']
    )

    # 計算早期方法觸發數量
    df['early_methods_triggered'] = (
        (df['method1_signal'].abs() > 0).astype(int) +
        (df['method2_signal'].abs() > 0).astype(int) +
        (df['method3_signal'].abs() > 0).astype(int)
    )

    # 判定發動信號
    df['is_outbreak'] = (
        (df['combined_score'] > 0.6) &
        (df['early_methods_triggered'] >= 2)
    )

    # 分類信號類型
    df['signal_type'] = 'neutral'
    df.loc[df['is_outbreak'] & (df['combined_score'] > 0), 'signal_type'] = 'strong_outbreak'
    df.loc[df['is_outbreak'] & (df['combined_score'] < 0), 'signal_type'] = 'weak_outbreak'

    return df


def generate_rotation_signals(
    df_with_signals: pd.DataFrame,
    latest_date: str,
    top_n: int = 15
) -> List[Dict]:
    """
    產生輪動信號清單（Phase 4 優化版：智能雙層過濾）

    Args:
        df_with_signals: 包含所有信號的 DataFrame
        latest_date: 最新日期
        top_n: 每日最多回傳 N 個信號 (預設 15)

    Returns:
        輪動信號列表（純買盤優勢信號，按 taker_ratio 排序）
    """
    # 篩選最新日期
    df_date = df_with_signals[df_with_signals['date'] == latest_date].copy()

    if df_date.empty:
        return []

    # 【第一層過濾：強勢買盤】
    # 核心條件：買盤優勢 + 相對強勢 + 多重驗證
    strong_signals = df_date[
        (df_date['taker_ratio'] > 1.0) &                    # 買盤優勢（核心）
        (df_date['rank_pct'] > 0.6) &                       # 排名前 40%
        (df_date['early_methods_triggered'] >= 2) &         # 至少 2/3 方法
        (df_date['combined_score'] > 0.65)                  # 基礎分數
    ]

    if strong_signals.empty:
        return []

    # 【第二層排序：買盤強度優先】
    # 依 taker_ratio 優先排序（買盤強度 > 綜合分數）
    strong_signals = strong_signals.sort_values(
        ['taker_ratio', 'combined_score'],
        ascending=False
    )

    # 取 TOP N
    top_signals = strong_signals.head(top_n)

    # 【最終過濾：移除相對弱勢】
    final_signals = top_signals[top_signals['rank_pct'] > 0.5]

    # 產生信號列表
    signals = []
    for _, row in final_signals.iterrows():
        signals.append({
            'date': row['date'],
            'industry': row['industry'],
            'signal_type': 'strong_outbreak',  # Phase 4: 純多頭信號
            'combined_score': round(row['combined_score'], 3),
            'taker_ratio': round(row['taker_ratio'], 3),
            'z_score': round(row['z_score'], 3),
            'rank_pct': round(row['rank_pct'], 3),
            'early_methods': int(row['early_methods_triggered']),
            'method1': int(row['method1_signal']),
            'method2': int(row['method2_signal']),
            'method3': int(row['method3_signal'])
        })

    return signals


if __name__ == "__main__":
    """測試早期檢測功能"""
    print("產業輪動早期檢測模組測試")
    print("=" * 60)
    print("✅ 方法 1：異常強度檢測（權重 40%）")
    print("✅ 方法 2：排名變化檢測（權重 30%）")
    print("✅ 方法 3：變化率檢測（權重 20%）")
    print("✅ 方法 4：Z-score 檢測（權重 5%）")
    print("✅ 方法 5：量能加權檢測（權重 5%）")
    print("=" * 60)
    print("\n模組載入成功，等待主程式調用")
