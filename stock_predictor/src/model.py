"""
LSTM 股票预测模型
双层 LSTM + Dropout + Dense 输出
"""
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models"


def build_model(input_shape: tuple) -> Sequential:
    """
    构建双层 LSTM 模型

    Args:
        input_shape: (window, n_features)
    """
    model = Sequential([
        Input(shape=input_shape),
        LSTM(128, return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def get_callbacks():
    return [
        EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, verbose=0)
    ]


def save_model(model, ticker: str):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / f"{ticker}_lstm.keras"
    model.save(path)
    return path


def load_saved_model(ticker: str):
    path = MODEL_DIR / f"{ticker}_lstm.keras"
    if not path.exists():
        raise FileNotFoundError(f"模型文件不存在：{path}")
    return load_model(path)
