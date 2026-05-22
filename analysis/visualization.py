import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, Sequence


def plot_price_and_sma(
    df: pd.DataFrame,
    symbol: str,
    windows: Sequence[int] = (20, 50),
    save_path: Optional[str] = None,
) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=1.5)
    for window in windows:
        label = f"SMA_{window}"
        if label in df.columns:
            plt.plot(df["Date"], df[label], label=label, linewidth=1.0)
    plt.title(f"{symbol} Close Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    else:
        plt.show()
    plt.close()
