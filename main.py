import argparse
import logging
import os
from typing import Dict, List, Optional

import pandas as pd

from data import fetch_multiple_symbols
from analysis import add_technical_indicators, plot_price_and_sma
from utils import TOP_US_STOCKS, DEFAULT_SOURCE, save_prices_to_csv


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def analyze_symbol(
    symbol: str,
    df: pd.DataFrame,
    save_folder: Optional[str] = None,
    plot: bool = False,
) -> pd.DataFrame:
    df = add_technical_indicators(df)
    logger.info("\n=== %s ===", symbol)
    logger.info("Latest close: %0.2f", df["Close"].iloc[-1])
    logger.info("Latest RSI: %0.2f", df["RSI_14"].iloc[-1])
    logger.info("20-day volatility: %0.4f", df["Volatility_20"].iloc[-1])

    # Forecasting removed in portfolio version

    if save_folder:
        saved_path = save_prices_to_csv(df, save_folder, symbol)
        logger.info("Saved price data to %s", saved_path)

    if plot:
        plot_price_and_sma(df, symbol)

    return df


def main():
    parser = argparse.ArgumentParser(description="Simple stock analytics project")
    parser.add_argument("--symbols", nargs="*", help="Stock symbols to analyze")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Data source to use")
    parser.add_argument("--period", default="1y", help="History period to download")
    parser.add_argument("--interval", default="1d", help="Data interval")
    parser.add_argument("--save-csv", action="store_true", help="Save fetched data to CSV files")
    parser.add_argument("--plot", action="store_true", help="Show a plot for each symbol")
    args = parser.parse_args()

    symbols: List[str] = args.symbols or TOP_US_STOCKS
    logger.info("Fetching %s symbols from %s", len(symbols), args.source)
    symbols_data: Dict[str, pd.DataFrame] = fetch_multiple_symbols(
        symbols, source=args.source, period=args.period, interval=args.interval
    )

    save_folder: Optional[str] = os.path.join("data", "prices") if args.save_csv else None

    for symbol, df in symbols_data.items():
        if df.empty:
            logger.warning("No data for %s, skipping", symbol)
            continue
        analyze_symbol(symbol, df, save_folder=save_folder, plot=args.plot)


if __name__ == "__main__":
    main()
