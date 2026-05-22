# Stock Forecasting Portfolio Project

A portfolio-ready Python application that demonstrates data engineering, technical analysis, forecasting, and interactive visualization for equity markets.

![Project Dashboard](newplot.png)

## 🎯 Why this project matters

This repository was built as a portfolio showcase to demonstrate:

- end-to-end data collection and preprocessing for financial time series
- implementation of trading analytics and risk indicators
- simple forecasting model design and comparison
- user-facing product delivery with an interactive Streamlit dashboard
- modular code organization that is easy to extend and maintain

## 🔥 Key Highlights

- Historical price retrieval for multiple US stocks using `yfinance`
- Technical indicators computed in reusable analysis functions:
  - 20-day / 50-day moving averages
  - 14-day RSI
  - annualized 20-day volatility
- Forecast generation via:
  - naive persistence model
  - moving average projection
- Streamlit dashboard for data exploration, charting, and CSV export
- Clean package structure that separates data, analysis, models, and utilities

## 🧠 Skills demonstrated

- Python data engineering with `pandas`
- time series analysis and financial indicator development
- visualization with Plotly and Streamlit
- modular application design and reusable code
- CLI development and dashboard deployment
- version-controlled project structure for portfolio presentation

## 📚 Project Structure

- `main.py` — command-line analysis workflow
- `dashboard.py` — Streamlit visualization and export app
- `data/` — price fetcher and source configuration
- `analysis/` — indicator calculations and helper logic
- `models/` — forecasting algorithms
- `utils/` — constants and CSV export utilities

## 🚀 Run the project

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the command-line analysis:

```bash
python main.py
```

4. Launch the dashboard:

```bash
streamlit run dashboard.py
```

## 💻 Example usage

Analyze specific stocks:

```bash
python main.py --symbols AAPL MSFT TSLA
```

Run a 10-day forecast:

```bash
python main.py --forecast-days 10
```

Export analyzed data:

```bash
python main.py --save-csv
```

## 📈 What the dashboard shows

- Price chart with overlaid SMA 20 and SMA 50
- RSI indicator with overbought/oversold thresholds
- Forecast comparison between naive and moving-average models
- Downloadable CSV export of analyzed data

## 🔧 Why this is portfolio-ready

This project is designed to show both technical depth and product maturity:

- clean modular architecture across packages
- real-world data integration
- hands-on analytics and visual storytelling
- a polished interactive dashboard for non-technical audiences
- clear project goals, usage instructions, and extension opportunities

## 🚧 Future improvements

Potential portfolio enhancements:

- add backtesting and forecast validation metrics
- include additional models such as ARIMA, Prophet, or LSTM
- support multiple data sources beyond Yahoo Finance
- add unit tests and CI automation
- include more advanced dashboard insights like risk heatmaps or portfolio allocation

## 📦 Requirements

- Python 3.11+
- pandas
- numpy
- matplotlib
- yfinance
- requests
- streamlit
- plotly
