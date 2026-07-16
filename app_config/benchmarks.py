from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Benchmark:

    name: str
    ticker: str
    currency: str = "INR"


BENCHMARKS = {

    "NIFTY 50": Benchmark(
        name="NIFTY 50",
        ticker="^NSEI",
    ),

    "NIFTY NEXT 50": Benchmark(
        name="NIFTY NEXT 50",
        ticker="^NSMIDCP",
    ),

    "NIFTY 500": Benchmark(
        name="NIFTY 500",
        ticker="^CRSLDX",
    ),

    "NIFTY MIDCAP 150": Benchmark(
        name="NIFTY MIDCAP 150",
        ticker="NIFTY_MIDCAP_150.NS",
    ),

    "SENSEX": Benchmark(
        name="SENSEX",
        ticker="^BSESN",
    ),

    "NASDAQ 100": Benchmark(
        name="NASDAQ 100",
        ticker="^NDX",
        currency="USD",
    ),

    "S&P 500": Benchmark(
        name="S&P 500",
        ticker="^GSPC",
        currency="USD",
    ),

    "DOW JONES": Benchmark(
        name="Dow Jones",
        ticker="^DJI",
        currency="USD",
    ),
}