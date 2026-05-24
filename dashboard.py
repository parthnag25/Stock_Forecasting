import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from data import fetch_multiple_symbols
from analysis import add_technical_indicators
from models import (
    naive_forecast,
    moving_average_forecast,
    estimate_future_price,
    calculate_expected_return,
    forecast_direction,
    signal_from_indicators,
    confidence_from_volatility,
    model_performance_metrics,
)
from utils import TOP_US_STOCKS, save_prices_to_csv


def _build_signal_reason(expected_return: float, rsi: float, sma_20: float, sma_50: float, volatility: float) -> str:
    parts = []
    if expected_return > 0:
        parts.append("The model projects a positive future return.")
    elif expected_return < 0:
        parts.append("The model projects a downward move.")
    else:
        parts.append("The forecast outlook is flat.")

    if sma_20 > sma_50:
        parts.append("The 20-day moving average is above the 50-day moving average.")
    else:
        parts.append("The 20-day moving average is below the 50-day moving average.")

    if rsi < 70:
        parts.append("RSI remains below the overbought threshold.")
    else:
        parts.append("RSI is near or above overbought levels.")

    if volatility < 20:
        parts.append("Volatility is low, supporting higher confidence.")
    elif volatility < 35:
        parts.append("Volatility is moderate, so treat the signal as an analytical estimate.")
    else:
        parts.append("Volatility is elevated, so interpret the outlook with caution.")

    return " ".join(parts)


st.set_page_config(page_title="Stock Forecasting & Market Outlook Dashboard", layout="wide")
st.title("📈 Stock Forecasting & Market Outlook Dashboard")
st.markdown(
    "This dashboard analyzes historical stock trends, technical indicators, and future price outlooks "
    "for selected U.S. stocks using Python, Streamlit, and baseline forecasting models."
)

# Sidebar configuration
st.sidebar.header("Configuration")
selected_symbols = st.sidebar.multiselect(
    "Select stocks to analyze:",
    TOP_US_STOCKS,
    default=["AAPL", "MSFT"]
)

period = st.sidebar.selectbox("Historical period:", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
forecast_days = st.sidebar.slider("Forecast days:", 1, 30, 5)
save_data = st.sidebar.checkbox("Save data to CSV")

if not selected_symbols:
    st.warning("Please select at least one stock to analyze.")
    st.stop()

# Fetch data
st.sidebar.info(f"Fetching data for {len(selected_symbols)} stock(s)...")
symbols_data = fetch_multiple_symbols(selected_symbols, period=period)

if not symbols_data:
    st.error("Failed to fetch data. Please try again.")
    st.stop()

# Main tabs
tab1, tab2, tab3 = st.tabs([
    "Price & Indicators",
    "Forecast & Outlook",
    "Data Export",
])

with tab1:
    st.header("Historical Price Trend")
    selected_symbol = st.selectbox("Select a stock to view:", selected_symbols, key="chart_select")

    if selected_symbol in symbols_data:
        df = symbols_data[selected_symbol]
        df = add_technical_indicators(df)
        latest = df.iloc[-1]

        # Price chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Close"],
            mode="lines", name="Close Price",
            line=dict(color="blue", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["SMA_20"],
            mode="lines", name="SMA 20",
            line=dict(color="orange", width=1, dash="dash")
        ))
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["SMA_50"],
            mode="lines", name="SMA 50",
            line=dict(color="red", width=1, dash="dash")
        ))
        fig.update_layout(
            title=f"{selected_symbol} Price and Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=520,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Technical Indicators")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${latest['Close']:.2f}")
        with col2:
            st.metric("20-day SMA", f"${latest['SMA_20']:.2f}")
        with col3:
            st.metric("RSI (14)", f"{latest['RSI_14']:.2f}")
        with col4:
            st.metric("Volatility (20d)", f"{latest['Volatility_20']:.4f}")

        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=df["Date"], y=df["RSI_14"],
            mode="lines", name="RSI 14",
            line=dict(color="purple", width=2)
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
        fig_rsi.update_layout(
            title=f"{selected_symbol} RSI (14)",
            xaxis_title="Date",
            yaxis_title="RSI",
            hovermode="x unified",
            height=420,
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

with tab2:
    st.header("Future Price Forecast")
    selected_symbol_forecast = st.selectbox("Select a stock for forecast:", selected_symbols, key="forecast_select")

    if selected_symbol_forecast in symbols_data:
        df = symbols_data[selected_symbol_forecast]
        df = add_technical_indicators(df)
        latest = df.iloc[-1]

        forecast_df = estimate_future_price(df, days=forecast_days)
        forecast_price = forecast_df["Forecast"].iloc[-1]
        expected_change = forecast_price - latest["Close"]
        expected_return = calculate_expected_return(latest["Close"], forecast_price)
        direction = forecast_direction(expected_return)
        signal = signal_from_indicators(
            expected_return,
            latest["RSI_14"],
            latest["SMA_20"],
            latest["SMA_50"],
        )
        confidence = confidence_from_volatility(latest["Volatility_20"])

        hist_data = df[["Date", "Close"]].tail(40).copy()
        hist_data.columns = ["Date", "Price"]

        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=hist_data["Date"], y=hist_data["Price"],
            mode="lines", name="Historical Price",
            line=dict(color="blue", width=2)
        ))
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Date"], y=forecast_df["Forecast"],
            mode="lines+markers", name="Forecasted Price",
            line=dict(color="green", width=2, dash="dash")
        ))
        fig_forecast.update_layout(
            title=f"{selected_symbol_forecast} {forecast_days}-Day Forecast",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=520,
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        st.subheader("Forecast Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${latest['Close']:.2f}")
            st.metric("Forecast Direction", direction)
        with col2:
            st.metric("Forecasted Price", f"${forecast_price:.2f}", delta=f"${expected_change:.2f}")
            st.metric("Model-Based Signal", signal)
        with col3:
            st.metric("Expected Return %", f"{expected_return:+.2f}%")
            st.metric("Confidence Level", confidence)

        st.markdown(
            "**Reason:** " + _build_signal_reason(
                expected_return,
                latest["RSI_14"],
                latest["SMA_20"],
                latest["SMA_50"],
                latest["Volatility_20"],
            )
        )

        st.subheader("Model-Based Signal")
        st.write(
            "The dashboard derives a signal from expected return, RSI, moving average trend, and volatility. "
            "This is an analytical output, not financial advice."
        )

        st.subheader("Model Performance")
        perf_df = model_performance_metrics(df)
        st.write("Baseline model error metrics for historical prices and simple forecasting methods.")
        st.dataframe(perf_df, use_container_width=True)

with tab3:
    st.header("CSV Export")
    st.info("Select a stock and download its analyzed data as CSV.")

    export_symbol = st.selectbox("Select stock to export:", selected_symbols, key="export_select")
    if export_symbol in symbols_data:
        df = symbols_data[export_symbol]
        df = add_technical_indicators(df)
        export_df = df.copy()
        export_df["Date"] = export_df["Date"].astype(str)

        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label=f"Download {export_symbol} data as CSV",
            data=csv_data,
            file_name=f"{export_symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        st.write(f"Preview of {export_symbol} data:")
        st.dataframe(export_df.head(10), use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "**Disclaimer:** This dashboard is for educational and analytical purposes only. "
    "It does not provide financial advice or investment recommendations. Forecasts are model-based estimates and may be inaccurate."
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Stock Forecasting & Market Outlook Dashboard**  \nBuilt with Streamlit & Plotly")
