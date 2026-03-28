"""
股票数据采集模块
使用 yfinance 下载历史股价数据
"""
import yfinance as yf
import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


def fetch_stock_data(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    下载股票历史数据

    Args:
        ticker: 股票代码，如 'AAPL', '0700.HK', '600519.SS'
        period: 时间跨度，如 '1y', '2y', '5y'

    Returns:
        包含 OHLCV 数据的 DataFrame
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if df.empty:
        raise ValueError(f"未找到股票数据：{ticker}")

    df.index = pd.to_datetime(df.index)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    return df


def save_data(df: pd.DataFrame, ticker: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{ticker}.csv"
    df.to_csv(path)
    return path


def load_data(ticker: str) -> pd.DataFrame:
    path = DATA_DIR / f"{ticker}.csv"
    if not path.exists():
        raise FileNotFoundError(f"本地无缓存数据，请先运行 fetch_stock_data('{ticker}')")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df
