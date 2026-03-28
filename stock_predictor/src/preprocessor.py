"""
数据预处理与特征工程模块
- 技术指标：MA、EMA、RSI、MACD、Bollinger Bands
- 归一化
- 构造 LSTM 时序窗口
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]

    # 移动平均
    df["MA5"]  = close.rolling(5).mean()
    df["MA20"] = close.rolling(20).mean()
    df["EMA12"] = close.ewm(span=12, adjust=False).mean()
    df["EMA26"] = close.ewm(span=26, adjust=False).mean()

    # MACD
    df["MACD"]   = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # RSI (14)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss + 1e-9)
    df["RSI"] = 100 - 100 / (1 + rs)

    # Bollinger Bands
    df["BB_mid"]   = close.rolling(20).mean()
    df["BB_upper"] = df["BB_mid"] + 2 * close.rolling(20).std()
    df["BB_lower"] = df["BB_mid"] - 2 * close.rolling(20).std()

    # 收益率
    df["Return"] = close.pct_change()

    df.dropna(inplace=True)
    return df


FEATURE_COLS = [
    "Open", "High", "Low", "Close", "Volume",
    "MA5", "MA20", "MACD", "Signal", "RSI",
    "BB_upper", "BB_lower", "Return"
]


def build_sequences(df: pd.DataFrame, window: int = 60):
    """
    将时序数据切割为 (X, y) 序列

    Args:
        df: 含特征列的 DataFrame
        window: 回看窗口（天数）

    Returns:
        X: shape (n, window, features)
        y: shape (n,)  — 下一天收盘价（归一化后）
        scaler: 用于反归一化
        feature_cols: 使用的特征列名
    """
    data = df[FEATURE_COLS].values
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    close_idx = FEATURE_COLS.index("Close")
    X, y = [], []
    for i in range(window, len(data_scaled)):
        X.append(data_scaled[i - window:i])
        y.append(data_scaled[i, close_idx])

    return np.array(X), np.array(y), scaler


def train_test_split_ts(X, y, test_ratio: float = 0.2):
    """时序数据切分（不随机打乱）"""
    split = int(len(X) * (1 - test_ratio))
    return X[:split], X[split:], y[:split], y[split:]
