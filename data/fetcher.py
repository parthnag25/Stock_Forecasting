import logging
from typing import Dict, List

import pandas as pd
import yfinance as yf

from .sources import SUPPORTED_SOURCES

logger = logging.getLogger(__name__)


def fetch_price_history(symbol: str, source: str = "yahoo", period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical price data for a single symbol."""
    source = source.lower()
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"Unsupported source: {source}. Supported sources: {SUPPORTED_SOURCES}")

    if source == "yahoo":
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            raise RuntimeError(f"No data returned for {symbol} from Yahoo Finance")
        df = df.reset_index()
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        return df

    logger.warning("Source %s is not implemented beyond Yahoo Finance. Falling back to Yahoo Finance.", source)
    return fetch_price_history(symbol, source="yahoo", period=period, interval=interval)


def fetch_multiple_symbols(symbols: List[str], source: str = "yahoo", period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """Fetch historical data for multiple symbols."""
    results: Dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        try:
            results[symbol] = fetch_price_history(symbol, source=source, period=period, interval=interval)
        except Exception as exc:
            logger.error("Failed to fetch %s: %s", symbol, exc)
    return results
