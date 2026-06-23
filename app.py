import akshare as ak
import pandas as pd
import mplfinance as mpf
import streamlit as st

# 页面配置，适配手机屏幕
st.set_page_config(
    page_title="玉米期货K线",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🌽 玉米期货K线（黑白裸K）")
st.caption("数据来源：新浪财经 | 自动更新 | 无均线无网格")

# 底部切换按钮，手机操作方便
period = st.radio(
    "选择周期",
    ["日K（日盘+当日夜盘）", "周K（周五锚点·阴阳线对齐）"],
    horizontal=True
)

@st.cache_data(ttl=3600)  # 缓存1小时，不用每次刷都拉数据，速度更快
def load_and_process_data():
    """拉取并处理数据，和你之前的脚本逻辑完全一致"""
    try:
        df = ak.futures_main_sina(symbol="C0", start_date="20200101")
        # 数据清洗（和你之前的代码一模一样）
        col_map = {"日期": "Date", "开盘价": "Open", "最高价": "High", "最低价": "Low", "收盘价": "Close"}
        df = df.rename(columns=col_map)
        df["Date"] = pd.to_datetime(df["Date"])
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values("Date").set_index("Date").dropna(subset=["Open", "Close"])
        return df
    except Exception as e:
        st.error(f"数据拉取失败：{e}，请稍后重试")
        return None

df = load_and_process_data()

if df is not None:
    # 黑白裸K样式（完全保留你之前的要求）
    mc = mpf.make_marketcolors(up="white", down="black", edge="black", wick="black")
    style = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle="",
        facecolor="white",
        rc={"axes.labelcolor": "black", "axes.titlecolor": "black"}
    )
    
    if period == "日K（日盘+当日夜盘）":
        st.subheader("日K线（当日夜盘归当日）")
        fig, axes = mpf.plot(
            df.tail(60),  # 显示最近60根日K
            type="candle",
            style=style,
            returnfig=True,
            figsize=(10, 6)
        )
        for ax in axes: ax.grid(False)
        st.pyplot(fig)
        st.caption(f"最近60根日K | 最后更新：{df.index[-1].strftime('%Y-%m-%d %H:%M')}")
        
    else:  # 周K
        st.subheader("周K线（周五锚点·阴阳线对齐）")
        weekly_df = df.resample("W-FRI", label="right", closed="right").agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last"),
        ).dropna(subset=["Open", "Close"])
        
        fig, axes = mpf.plot(
            weekly_df.tail(50),  # 显示最近50根周K
            type="candle",
            style=style,
            returnfig=True,
            figsize=(10, 6)
        )
        for ax in axes: ax.grid(False)
        st.pyplot(fig)
        st.caption(f"最近50根周K | 最后一周锚点：{weekly_df.index[-1].strftime('%Y-%m-%d')}")

st.markdown("---")
st.caption("⚠️ 免责声明：本工具仅供技术研究使用，不构成任何投资建议。期货交易有风险，决策需谨慎。")