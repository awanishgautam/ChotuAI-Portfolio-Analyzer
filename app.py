from __future__ import annotations

import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

from components.login import login
from domain.enums import AssetType
from services.benchmark_service import BenchmarkService
from analytics.benchmark_metrics import BenchmarkMetrics
from agents.portfolio_agent import PortfolioAgent
from analytics.risk.risk_engine import RiskEngine
from portfolio.history_builder import PortfolioHistoryBuilder
from portfolio.portfolio_engine import PortfolioEngine
from brokers import BrokerType
from providers.broker_provider_factory import ProviderFactory
from app_config import settings

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="AI Portfolio Analyzer",
    layout="wide",
)

broker_param = st.query_params.get("broker")

if broker_param == "ICICI_DIRECT":

    st.session_state.broker = BrokerType.ICICI_DIRECT

elif broker_param == "ZERODHA":

    st.session_state.broker = BrokerType.ZERODHA

# ----------------------------------------------------
# Broker Selection
# ----------------------------------------------------
if "broker" not in st.session_state:

    st.session_state.broker = BrokerType.ZERODHA

broker = st.sidebar.selectbox(
    "Broker",
    [
        BrokerType.ZERODHA,
        BrokerType.ICICI_DIRECT,
    ],
    index=[
        BrokerType.ZERODHA,
        BrokerType.ICICI_DIRECT,
    ].index(
        st.session_state.broker
    ),
    format_func=lambda x: {
        BrokerType.ZERODHA: "Zerodha",
        BrokerType.ICICI_DIRECT: "ICICI Direct",
    }[x],
)

# ----------------------------------------------------
# Authentication
# ----------------------------------------------------

if (
    "broker" in st.session_state
    and
    st.session_state.broker != broker
):

    keys_to_remove = [
        "access_token",
        "portfolio",
        "metrics",
        "portfolio_prices",
        "benchmark_prices",
        "benchmark_metrics",
    ]

    for key in keys_to_remove:

        st.session_state.pop(
            key,
            None,
        )

st.session_state.broker = broker

login(
    st.session_state.broker,
)

# ----------------------------------------------------
# Title and Sidebars
# ----------------------------------------------------
st.title("📈 AI Portfolio Analyzer")

asset_option = st.sidebar.radio(
    "Asset Type",
    [
        "All",
        "Equity",
        "Mutual Fund",
    ],
)

refresh_clicked = st.button("🔄 Refresh Portfolio")

benchmark_service = BenchmarkService()

benchmark_name = st.sidebar.selectbox(
    "Benchmark",
    benchmark_service.available(),
    index=0,
)

st.sidebar.toggle(
    "💰 Show monetary values",
    key="show_amounts",
)

# ----------------------------------------------------
# Session State
# ----------------------------------------------------

if "portfolio" not in st.session_state:
    st.session_state.portfolio = None

if "metrics" not in st.session_state:
    st.session_state.metrics = None

if "portfolio_prices" not in st.session_state:
    st.session_state.portfolio_prices = None
    
if "benchmark_prices" not in st.session_state:
    st.session_state.benchmark_prices = None

if "benchmark_metrics" not in st.session_state:
    st.session_state.benchmark_metrics = None

if "benchmark_name" not in st.session_state:
    st.session_state.benchmark_name = benchmark_name

if "loaded_asset_option" not in st.session_state:
    st.session_state.loaded_asset_option = None

if "loaded_benchmark" not in st.session_state:
    st.session_state.loaded_benchmark = None

if "loaded_broker" not in st.session_state:
    st.session_state.loaded_broker = None
# ----------------------------------------------------
# Show / Hide Monetary Values
# ----------------------------------------------------

if "show_amounts" not in st.session_state:
    st.session_state.show_amounts = False

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------

def money(value: float) -> str:

    if not st.session_state.show_amounts:
        return "₹ •••••••"

    return f"₹{value:,.2f}"

# ----------------------------------------------------
# Refresh Portfolio
# ----------------------------------------------------
needs_refresh = (
    refresh_clicked
    or st.session_state.portfolio is None
    or st.session_state.loaded_asset_option != asset_option
    or st.session_state.loaded_benchmark != benchmark_name
    or st.session_state.loaded_broker != broker
)

if needs_refresh:

    if st.session_state.broker == BrokerType.ICICI_DIRECT:
        st.subheader("ICICI Direct APIs only support Equity. Mutual Funds Are not supported")
        
    with st.spinner("Downloading holdings..."):

        client = ProviderFactory.create(
            broker=broker,
            access_token=st.session_state.access_token,
        )

        portfolio_engine = PortfolioEngine(client)

        asset_type = None

        if asset_option == "Equity":
            asset_type = AssetType.EQUITY

        elif asset_option == "Mutual Fund":
            asset_type = AssetType.MUTUAL_FUND

        portfolio = portfolio_engine.build(
            asset_type=asset_type,
        )

        if not portfolio.holdings:
            st.warning("No mutual fund holdings found.")
            st.stop()

        history = PortfolioHistoryBuilder()

        portfolio_prices = history.build(portfolio)

        benchmark_prices = None
        benchmark_metrics = None
        metrics = None

        try:

            benchmark_prices = benchmark_service.history(
                benchmark_name,
                portfolio_prices.index.min(),
                portfolio_prices.index.max(),
            )

        except Exception as e:

            st.warning(
                f"Unable to download benchmark ({benchmark_name})\n\n{e}"
            )

        if portfolio_prices is not None:

            risk_engine = RiskEngine(
                portfolio_prices=portfolio_prices,
                benchmark_prices=benchmark_prices,
                benchmark_name=benchmark_name,
            )

            metrics = risk_engine.metrics()

            if benchmark_prices is not None:

                benchmark_metrics = BenchmarkMetrics(
                    portfolio_prices,
                    benchmark_prices,
                    benchmark_name,
                ).summary()

        st.session_state.portfolio = portfolio
        st.session_state.metrics = metrics
        st.session_state.portfolio_prices = portfolio_prices
        st.session_state.benchmark_prices = benchmark_prices
        st.session_state.benchmark_metrics = benchmark_metrics
        st.session_state.benchmark_name = benchmark_name

        st.session_state.loaded_asset_option = asset_option
        st.session_state.loaded_benchmark = benchmark_name
        st.session_state.loaded_broker = broker


# ----------------------------------------------------
# Portfolio Summary
# ----------------------------------------------------

if st.session_state.portfolio:

    summary = st.session_state.portfolio.summary()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Market Value",
        money(summary["market_value"]),
    )

    c2.metric(
        "Invested",
        money(summary["invested_value"]),
    )

    c2.metric(
        "PnL",
        money(summary["market_value"] - summary["invested_value"]),
    )

    c4.metric(
        "Return %",
        f"{summary['pnl_percent']:.2f}%",
    )


# ----------------------------------------------------
# Holdings
# ----------------------------------------------------

if st.session_state.portfolio:

    st.header("Holdings")

    df = st.session_state.portfolio.dataframe()
    # Sort by serial number (index)
    df = df.sort_index()

    if not st.session_state.show_amounts:

        for column in [
            "Quantity",
            "Average Price",
            "Last Price",
            "Invested",
            "Current Value",
            "PnL",
            "Allocation %",
        ]:

            if column in df.columns:

                df[column] = "••••••"

    st.dataframe(
        df,
        use_container_width=True,
    )

# ----------------------------------------------------
# PnL Distribution
# ----------------------------------------------------

if st.session_state.portfolio:

    df = st.session_state.portfolio.dataframe()

    if not df.empty and "PnL" in df.columns:

        profit_df = (
            df[df["PnL"] > 0]
            .copy()
            .sort_values(
                "PnL",
                ascending=False,
            )
        )

        loss_df = (
            df[df["PnL"] < 0]
            .copy()
            .sort_values(
                "PnL",
            )
        )

        st.header("PnL Distribution")

        left, right = st.columns(2)

        # -----------------------------------------
        # Profit Contributors
        # -----------------------------------------

        with left:

            st.subheader("🟢 Profit Contributors")

            if not profit_df.empty:

                fig = px.pie(
                    profit_df,
                    names="Name",
                    values="PnL",
                    hole=0.45,
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Profit: ₹%{value:,.2f}<br>"
                        "Contribution: %{percent}"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    margin=dict(
                        t=20,
                        b=20,
                        l=20,
                        r=20,
                    ),
                    showlegend=True,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No profitable holdings."
                )

        # -----------------------------------------
        # Loss Contributors
        # -----------------------------------------

        with right:

            st.subheader("🔴 Loss Contributors")

            if not loss_df.empty:

                loss_df["Loss"] = (
                    loss_df["PnL"].abs()
                )

                fig = px.pie(
                    loss_df,
                    names="Name",
                    values="Loss",
                    hole=0.45,
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Loss: ₹%{value:,.2f}<br>"
                        "Contribution: %{percent}"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    margin=dict(
                        t=20,
                        b=20,
                        l=20,
                        r=20,
                    ),
                    showlegend=True,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No loss-making holdings."
                )

# ----------------------------------------------------
# Top Profit / Loss Contributors
# ----------------------------------------------------

if st.session_state.portfolio:

    df = st.session_state.portfolio.dataframe()

    if not df.empty:

        st.header("Top PnL Contributors")

        left, right = st.columns(2)

        # ==========================================
        # Top Profit Contributors
        # ==========================================

        with left:

            st.subheader("🟢 Top Profit Contributors")

            profit_df = (
                df[df["PnL"] > 0]
                .copy()
                .sort_values(
                    "PnL",
                    ascending=False,
                )
                .head(10)
            )

            if not profit_df.empty:

                fig = px.bar(
                    profit_df,
                    x="PnL",
                    y="Name",
                    orientation="h",
                    text="PnL",
                )

                fig.update_layout(
                    yaxis={
                        "categoryorder": "total ascending",
                    },
                    xaxis_title="Profit (₹)",
                    yaxis_title="",
                    height=450,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20,
                    ),
                    showlegend=False,
                )

                fig.update_traces(
                    texttemplate="₹%{x:,.0f}",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Profit: ₹%{x:,.2f}"
                        "<extra></extra>"
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No profitable holdings."
                )

        # ==========================================
        # Top Loss Contributors
        # ==========================================

        with right:

            st.subheader("🔴 Top Loss Contributors")

            loss_df = (
                df[df["PnL"] < 0]
                .copy()
            )

            loss_df["Loss"] = (
                loss_df["PnL"].abs()
            )

            loss_df = (
                loss_df.sort_values(
                    "Loss",
                    ascending=False,
                )
                .head(10)
            )

            if not loss_df.empty:

                fig = px.bar(
                    loss_df,
                    x="Loss",
                    y="Name",
                    orientation="h",
                    text="Loss",
                )

                fig.update_layout(
                    yaxis={
                        "categoryorder": "total ascending",
                    },
                    xaxis_title="Loss (₹)",
                    yaxis_title="",
                    height=450,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20,
                    ),
                    showlegend=False,
                )

                fig.update_traces(
                    texttemplate="₹%{x:,.0f}",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Loss: ₹%{x:,.2f}"
                        "<extra></extra>"
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No loss-making holdings."
                )

# ----------------------------------------------------
# Portfolio Value
# ----------------------------------------------------

if st.session_state.portfolio_prices is not None:

    st.header("Portfolio Value")
    print((st.session_state.portfolio_prices == 0).sum())
    print(st.session_state.portfolio_prices.nsmallest(20))
    st.line_chart(
        st.session_state.portfolio_prices
    )

# ----------------------------------------------------
# Risk Metrics
# ----------------------------------------------------

if (
    st.session_state.metrics
    and
    asset_option != "All"
):

    st.header("Risk Metrics")

    metrics = st.session_state.metrics

    left, right = st.columns(2)

    with left:

        st.metric(
            "Sharpe",
            f"{metrics.sharpe_ratio:.2f}",
        )

        st.metric(
            "Sortino",
            f"{metrics.sortino_ratio:.2f}",
        )

        st.metric(
            "Volatility",
            f"{metrics.volatility:.2%}",
        )

        st.metric(
            "Max Drawdown",
            f"{metrics.max_drawdown:.2%}",
        )

    with right:

        st.metric(
            "Beta",
            f"{metrics.beta:.2f}",
        )

        st.metric(
            "Alpha",
            f"{metrics.alpha:.2%}",
        )

        st.metric(
            "Information Ratio",
            f"{metrics.information_ratio:.2f}",
        )

        st.metric(
            "Historical VaR",
            f"{metrics.historical_var:.2%}",
        )

# ----------------------------------------------------
# Benchmark Metrics
# ----------------------------------------------------
if (
    st.session_state.benchmark_metrics
    and
    asset_option != "All"
):

    bm = st.session_state.benchmark_metrics

    st.header("Benchmark Comparison")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Benchmark",
        st.session_state.benchmark_name,
    )

    c2.metric(
        "Portfolio CAGR",
        f"{bm.portfolio_cagr:.2%}",
    )

    c3.metric(
        "Benchmark CAGR",
        f"{bm.benchmark_cagr:.2%}",
    )

    c1.metric(
        "Alpha",
        f"{bm.alpha:.2%}",
    )

    c2.metric(
        "Beta",
        f"{bm.beta:.2f}",
    )

    c3.metric(
        "Correlation",
        f"{bm.correlation:.2f}",
    )

    c1.metric(
        "Tracking Error",
        f"{bm.tracking_error:.2%}",
    )

    c2.metric(
        "Information Ratio",
        f"{bm.information_ratio:.2f}",
    )

# ----------------------------------------------------
# Benchmark Chart
# ----------------------------------------------------
if (
    st.session_state.portfolio_prices is not None
    and
    st.session_state.benchmark_prices is not None
    and
    asset_option != "All"
):

    portfolio = st.session_state.portfolio_prices.copy()
    benchmark = st.session_state.benchmark_prices.copy()

    portfolio.index = pd.to_datetime(portfolio.index)
    benchmark.index = pd.to_datetime(benchmark.index)

    if portfolio.index.tz is not None:
        portfolio.index = portfolio.index.tz_localize(None)

    if benchmark.index.tz is not None:
        benchmark.index = benchmark.index.tz_localize(None)

    comparison = pd.concat(
        [
            portfolio.rename("Portfolio"),
            benchmark.rename(st.session_state.benchmark_name),
        ],
        axis=1,
    ).dropna()

    comparison = comparison / comparison.iloc[0]

    st.header("Portfolio vs Benchmark")

    st.line_chart(comparison)

# ----------------------------------------------------
# AI Chat
# ----------------------------------------------------

st.header("Ask AI")

question = st.text_input(
    "Ask about your portfolio"
)

if st.button("Ask"):

    if not question:

        st.warning("Enter a question.")

    elif st.session_state.portfolio is None:

        st.warning("Refresh portfolio first.")

    else:

        with st.spinner("Thinking..."):

            agent = PortfolioAgent(
                settings.openai_api_key.get_secret_value()
                if settings.openai_api_key
                else None
            )

            answer = agent.ask(
                question=question,
                portfolio=st.session_state.portfolio,
                portfolio_prices=st.session_state.portfolio_prices,
                benchmark_prices=st.session_state.benchmark_prices,
                benchmark_name=st.session_state.benchmark_name,
            )

        st.markdown(answer)
