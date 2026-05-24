import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from data import fetch_multiple_symbols
from analysis import add_technical_indicators
from models import naive_forecast, moving_average_forecast
from utils import TOP_US_STOCKS, save_prices_to_csv


st.set_page_config(page_title="Stock Forecasting Dashboard", layout="wide")
st.title("📈 Stock Forecasting Dashboard")

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
tab1, tab2, tab3 = st.tabs(["Price & Indicators", "Forecasts", "Data Export"])

with tab1:
    st.header("Price Chart & Technical Indicators")
    selected_symbol = st.selectbox("Select a stock to view:", selected_symbols, key="chart_select")
    
    if selected_symbol in symbols_data:
        df = symbols_data[selected_symbol]
        df = add_technical_indicators(df)
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add closing price
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Close"],
            mode="lines", name="Close Price",
            line=dict(color="blue", width=2)
        ))
        
        # Add SMA 20
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["SMA_20"],
            mode="lines", name="SMA 20",
            line=dict(color="orange", width=1, dash="dash")
        ))
        
        # Add SMA 50
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
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display indicators
        col1, col2, col3, col4 = st.columns(4)
        latest = df.iloc[-1]
        
        with col1:
            st.metric("Latest Close", f"${latest['Close']:.2f}")
        with col2:
            st.metric("20-day MA", f"${latest['SMA_20']:.2f}")
        with col3:
            st.metric("RSI (14)", f"{latest['RSI_14']:.2f}")
        with col4:
            st.metric("Volatility (20d)", f"{latest['Volatility_20']:.4f}")
        
        # RSI chart
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
            height=400
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

with tab2:
    st.header("Forecasts")
    selected_symbol_forecast = st.selectbox("Select a stock for forecast:", selected_symbols, key="forecast_select")
    
    if selected_symbol_forecast in symbols_data:
        df = symbols_data[selected_symbol_forecast]
        
        # Generate forecasts
        naive_fc = naive_forecast(df, days=forecast_days)
        ma_fc = moving_average_forecast(df, window=5, days=forecast_days)
        
        # Combine with recent history
        hist_data = df[["Date", "Close"]].tail(20).copy()
        hist_data.columns = ["Date", "Price"]
        
        fig_forecast = go.Figure()
        
        # Historical prices
        fig_forecast.add_trace(go.Scatter(
            x=hist_data["Date"], y=hist_data["Price"],
            mode="lines", name="Historical Price",
            line=dict(color="blue", width=2)
        ))
        
        # Naive forecast
        fig_forecast.add_trace(go.Scatter(
            x=naive_fc["Date"], y=naive_fc["Forecast"],
            mode="lines+markers", name="Naive Forecast",
            line=dict(color="orange", width=2)
        ))
        
        # MA forecast
        fig_forecast.add_trace(go.Scatter(
            x=ma_fc["Date"], y=ma_fc["Forecast"],
            mode="lines+markers", name="MA Forecast",
            line=dict(color="green", width=2)
        ))
        
        fig_forecast.update_layout(
            title=f"{selected_symbol_forecast} Price Forecast ({forecast_days} days)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=500
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Display forecast values
        st.subheader("Forecast Details")
        forecast_df = pd.DataFrame({
            "Date": naive_fc["Date"],
            "Naive Forecast": naive_fc["Forecast"].values,
            "MA Forecast": ma_fc["Forecast"].values
        })
        st.dataframe(forecast_df, use_container_width=True)

with tab3:
    st.header("Data Export")
    st.info("Select a stock and download its analyzed data as CSV.")
    
    export_symbol = st.selectbox("Select stock to export:", selected_symbols, key="export_select")
    
    if export_symbol in symbols_data:
        df = symbols_data[export_symbol]
        df = add_technical_indicators(df)
        
        # Convert date to string for CSV export
        export_df = df.copy()
        export_df["Date"] = export_df["Date"].astype(str)
        
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label=f"Download {export_symbol} data as CSV",
            data=csv_data,
            file_name=f"{export_symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.write(f"Preview of {export_symbol} data:")
        st.dataframe(export_df.head(10), use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Stock Forecasting Dashboard v1.0**  \nBuilt with Streamlit & Plotly")
