import numpy as np
import pandas as pd


def _business_days_forward(start_date: pd.Timestamp, days: int) -> pd.DatetimeIndex:
    start = pd.to_datetime(start_date) + pd.Timedelta(days=1)
    return pd.date_range(start=start, periods=days, freq="B")


def estimate_future_price(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    last_price = df["Close"].iloc[-1]
    returns = df["Close"].pct_change().dropna()
    avg_daily_return = returns.tail(20).mean() if not returns.empty else 0.0
    projected_price = last_price * ((1 + avg_daily_return) ** days)
    forecast_dates = _business_days_forward(df["Date"].iloc[-1], days)
    return pd.DataFrame({"Date": forecast_dates, "Forecast": [projected_price] * days})


def calculate_expected_return(current_price: float, forecasted_price: float) -> float:
    return ((forecasted_price - current_price) / current_price) * 100


def forecast_direction(expected_return: float) -> str:
    if expected_return > 1:
        return "Upward"
    if expected_return < -1:
        return "Downward"
    return "Flat"


def signal_from_indicators(expected_return: float, rsi: float, sma_20: float, sma_50: float) -> str:
    if expected_return > 3 and rsi < 70 and sma_20 > sma_50:
        return "Bullish"
    if expected_return < -3 or rsi > 75 or sma_20 < sma_50:
        return "Bearish"
    return "Neutral"


def confidence_from_volatility(volatility: float) -> str:
    if volatility < 20:
        return "High"
    if volatility < 35:
        return "Medium"
    return "Low"


def model_performance_metrics(df: pd.DataFrame, window: int = 5, lookback: int = 20) -> pd.DataFrame:
    eval_df = df[["Close"]].copy()
    eval_df["Naive"] = df["Close"].shift(1)
    eval_df["MA_Forecast"] = df["Close"].rolling(window=window, min_periods=1).mean().shift(1)
    eval_df = eval_df.dropna().tail(lookback)

    metrics = []
    for model_name, predictions in [("Naive", eval_df["Naive"]), ("Moving Average", eval_df["MA_Forecast"])]:
        actual = eval_df["Close"].values
        pred = predictions.values
        mae = np.mean(np.abs(actual - pred))
        rmse = np.sqrt(np.mean((actual - pred) ** 2))
        # avoid divide-by-zero
        mape = np.mean(np.abs((actual - pred) / np.where(actual == 0, 1, actual))) * 100
        metrics.append(
            {
                "Model": model_name,
                "MAE": round(mae, 4),
                "RMSE": round(rmse, 4),
                "MAPE (%)": round(mape, 2),
            }
        )

    return pd.DataFrame(metrics)
