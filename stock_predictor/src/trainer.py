"""
训练与评估模块
"""
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .data_collector import fetch_stock_data, save_data
from .preprocessor import add_technical_indicators, build_sequences, train_test_split_ts, FEATURE_COLS
from .model import build_model, get_callbacks, save_model

MODEL_DIR = Path(__file__).parent.parent / "models"


def train(ticker: str, window: int = 60, epochs: int = 100, batch_size: int = 32):
    """
    完整训练流程：下载数据 → 特征工程 → 训练 → 保存

    Returns:
        dict: 包含 mae、rmse 评估指标和 history
    """
    print(f"[1/5] 下载 {ticker} 数据...")
    df = fetch_stock_data(ticker, period="5y")
    save_data(df, ticker)

    print("[2/5] 特征工程...")
    df = add_technical_indicators(df)

    print("[3/5] 构造时序序列...")
    X, y, scaler = build_sequences(df, window=window)
    X_train, X_test, y_train, y_test = train_test_split_ts(X, y)

    # 保存 scaler
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_DIR / f"{ticker}_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print(f"[4/5] 训练 LSTM 模型 (训练集 {len(X_train)} 条, 测试集 {len(X_test)} 条)...")
    model = build_model(input_shape=(window, len(FEATURE_COLS)))
    history = model.fit(
        X_train, y_train,
        validation_split=0.1,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=get_callbacks(),
        verbose=1
    )

    print("[5/5] 评估模型...")
    y_pred = model.predict(X_test).flatten()
    close_idx = FEATURE_COLS.index("Close")
    n_features = len(FEATURE_COLS)

    def inverse_close(arr):
        dummy = np.zeros((len(arr), n_features))
        dummy[:, close_idx] = arr
        return scaler.inverse_transform(dummy)[:, close_idx]

    y_test_real = inverse_close(y_test)
    y_pred_real = inverse_close(y_pred)

    mae  = mean_absolute_error(y_test_real, y_pred_real)
    rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))
    mape = np.mean(np.abs((y_test_real - y_pred_real) / y_test_real)) * 100

    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAPE: {mape:.2f}%")

    save_model(model, ticker)
    return {
        "mae": mae, "rmse": rmse, "mape": mape,
        "history": history.history,
        "y_test": y_test_real,
        "y_pred": y_pred_real
    }
