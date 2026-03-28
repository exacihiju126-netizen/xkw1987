"""
Streamlit 股票预测可视化仪表盘
运行方式：streamlit run dashboard/app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_collector import fetch_stock_data, save_data, load_data
from src.preprocessor import add_technical_indicators, build_sequences, FEATURE_COLS
from src.model import build_model, get_callbacks, save_model, load_saved_model
from src.trainer import train

# ── 页面配置 ─────────────────────────────────────────────
st.set_page_config(
    page_title="股票预测系统",
    page_icon="📈",
    layout="wide"
)

st.title("📈 股票价格预测系统（LSTM）")
st.caption("技术指标 + 深度学习 | 数据来源：Yahoo Finance")

# ── 侧边栏 ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 参数设置")
    ticker  = st.text_input("股票代码", value="AAPL",
                             help="美股：AAPL / 港股：0700.HK / A股：600519.SS")
    period  = st.selectbox("历史数据范围", ["2y", "3y", "5y"], index=2)
    window  = st.slider("回看窗口（天）", 30, 120, 60)
    epochs  = st.slider("最大训练轮数", 20, 200, 100)
    run_btn = st.button("🚀 开始训练并预测", type="primary", use_container_width=True)

# ── 主区域 ───────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 K线图 & 技术指标", "🤖 预测结果", "📉 训练曲线"])

@st.cache_data(show_spinner="下载股票数据...")
def get_data(ticker, period):
    df = fetch_stock_data(ticker, period=period)
    save_data(df, ticker)
    return df

# ── Tab1：K线图 ──────────────────────────────────────────
with tab1:
    try:
        df_raw = get_data(ticker, period)
        df = add_technical_indicators(df_raw.copy())

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            row_heights=[0.55, 0.25, 0.20],
                            vertical_spacing=0.03)

        # 蜡烛图
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="K线"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA5"],
                                 line=dict(color="orange", width=1), name="MA5"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"],
                                 line=dict(color="blue", width=1), name="MA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"],
                                 line=dict(color="gray", width=1, dash="dash"), name="布林上轨"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"],
                                 line=dict(color="gray", width=1, dash="dash"), name="布林下轨",
                                 fill="tonexty", fillcolor="rgba(128,128,128,0.1)"), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],
                                 line=dict(color="purple", width=1.5), name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # 成交量
        colors = ["green" if c >= o else "red"
                  for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"],
                             marker_color=colors, name="成交量"), row=3, col=1)

        fig.update_layout(height=700, xaxis_rangeslider_visible=False,
                          legend=dict(orientation="h", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("最新收盘价", f"${df['Close'].iloc[-1]:.2f}")
        col2.metric("5日涨跌", f"{(df['Close'].iloc[-1]/df['Close'].iloc[-6]-1)*100:.2f}%")
        col3.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
        col4.metric("数据条数", len(df))

    except Exception as e:
        st.error(f"数据加载失败：{e}")

# ── Tab2：预测结果 ────────────────────────────────────────
with tab2:
    if run_btn:
        with st.spinner("训练中，请稍候..."):
            try:
                result = train(ticker, window=window, epochs=epochs)
                st.session_state["result"] = result
            except Exception as e:
                st.error(f"训练失败：{e}")

    if "result" in st.session_state:
        r = st.session_state["result"]
        c1, c2, c3 = st.columns(3)
        c1.metric("MAE",  f"{r['mae']:.4f}")
        c2.metric("RMSE", f"{r['rmse']:.4f}")
        c3.metric("MAPE", f"{r['mape']:.2f}%")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(y=r["y_test"], name="真实价格",
                                  line=dict(color="blue")))
        fig2.add_trace(go.Scatter(y=r["y_pred"], name="预测价格",
                                  line=dict(color="red", dash="dot")))
        fig2.update_layout(title="测试集：真实 vs 预测",
                           xaxis_title="时间步", yaxis_title="价格",
                           height=420)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("点击左侧「开始训练并预测」按钮后，结果将显示在这里。")

# ── Tab3：训练曲线 ────────────────────────────────────────
with tab3:
    if "result" in st.session_state:
        hist = st.session_state["result"]["history"]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(y=hist["loss"], name="训练 Loss"))
        fig3.add_trace(go.Scatter(y=hist["val_loss"], name="验证 Loss"))
        fig3.update_layout(title="训练 / 验证 Loss 曲线",
                           xaxis_title="Epoch", yaxis_title="MSE Loss",
                           height=400)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("训练完成后，损失曲线将显示在这里。")
