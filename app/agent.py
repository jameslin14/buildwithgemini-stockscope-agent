# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore
from google.genai import types

from .a2ui_utils import a2ui_callback
from .prompt import INSTRUCTION


MODEL = "gemini-3.8-flash"
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-c7f7b6dbf6e7"

# Initialize Firestore client with explicit project ID string
db = firestore.Client(project=FIRESTORE_PROJECT_ID)
stocks_collection = db.collection("stocks")


def get_stock(ticker: str) -> Dict[str, Any]:
    """Retrieve financial metrics, valuation ratios, and notes for a stock by ticker symbol.

    Args:
        ticker: The stock ticker symbol (e.g. GOOGL, AAPL, NVDA, MSFT, AMZN).

    Returns:
        A dictionary containing company name, price, P/E ratio, forward P/E, EPS,
        market cap, dividend yield, profit margin, debt-to-equity, and 52-week range.
    """
    clean_ticker = ticker.strip().upper()
    doc = stocks_collection.document(clean_ticker).get()
    if not doc.exists:
        return {
            "error": f"Stock '{clean_ticker}' not found in the database. Use list_stocks to view tracked stocks, or save_stock to add it."
        }
    data = doc.to_dict()
    return data


def list_stocks(max_results: int = 10) -> List[Dict[str, Any]]:
    """List tracked stocks with their current price, P/E ratio, EPS, and market cap.

    Args:
        max_results: The maximum number of stocks to return (default 10).

    Returns:
        A list of stock summaries from Firestore.
    """
    docs = stocks_collection.limit(max_results).stream()
    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append(
            {
                "ticker": d.get("ticker"),
                "company_name": d.get("company_name"),
                "sector": d.get("sector"),
                "current_price": d.get("current_price"),
                "pe_ratio": d.get("pe_ratio"),
                "eps": d.get("eps"),
                "market_cap": d.get("market_cap"),
            }
        )
    return results


def save_stock(
    ticker: str,
    company_name: str,
    current_price: float,
    pe_ratio: float,
    eps: float,
    sector: str = "Technology",
    forward_pe: Optional[float] = None,
    market_cap: str = "N/A",
    dividend_yield: float = 0.0,
    profit_margin: float = 0.0,
    debt_to_equity: float = 0.0,
    fifty_two_week_high: Optional[float] = None,
    fifty_two_week_low: Optional[float] = None,
    analysis_notes: str = "",
) -> Dict[str, Any]:
    """Add or update stock valuation metrics and analysis notes in Firestore.

    Args:
        ticker: Ticker symbol (e.g. TSLA).
        company_name: Name of the company.
        current_price: Latest share price in USD.
        pe_ratio: Trailing price-to-earnings ratio.
        eps: Earnings per share in USD.
        sector: Company industry sector.
        forward_pe: Estimated forward P/E ratio.
        market_cap: Market capitalization (e.g. '1.5T' or '500B').
        dividend_yield: Annual dividend yield percentage (e.g. 1.5 for 1.5%).
        profit_margin: Net profit margin percentage.
        debt_to_equity: Total debt divided by shareholder equity.
        fifty_two_week_high: 52-week high share price.
        fifty_two_week_low: 52-week low share price.
        analysis_notes: Investment notes or thesis about this stock.

    Returns:
        Confirmation message with saved stock details.
    """
    clean_ticker = ticker.strip().upper()
    stock_payload = {
        "ticker": clean_ticker,
        "company_name": company_name,
        "sector": sector,
        "current_price": float(current_price),
        "pe_ratio": float(pe_ratio),
        "forward_pe": float(forward_pe) if forward_pe is not None else float(pe_ratio),
        "eps": float(eps),
        "market_cap": market_cap,
        "dividend_yield": float(dividend_yield),
        "profit_margin": float(profit_margin),
        "debt_to_equity": float(debt_to_equity),
        "fifty_two_week_high": float(fifty_two_week_high) if fifty_two_week_high is not None else float(current_price),
        "fifty_two_week_low": float(fifty_two_week_low) if fifty_two_week_low is not None else float(current_price),
        "analysis_notes": analysis_notes,
        "updated_at": datetime.datetime.now(ZoneInfo("UTC")).isoformat(),
    }
    stocks_collection.document(clean_ticker).set(stock_payload)
    return {"status": "success", "message": f"Saved stock '{clean_ticker}' ({company_name}) to Firestore.", "stock": stock_payload}


def calculate_valuation_metrics(
    ticker: str,
    expected_growth_rate: float = 12.0,
    required_rate_of_return: float = 10.0,
    margin_of_safety_target: float = 20.0,
) -> Dict[str, Any]:
    """Calculate valuation multiples, PEG ratio, Graham fair value, and investment determination.

    Args:
        ticker: The stock ticker symbol (e.g. GOOGL, AAPL, NVDA, MSFT, AMZN).
        expected_growth_rate: Estimated annual EPS growth rate percentage for the next 5 years (default 12.0%).
        required_rate_of_return: Desired discount rate / hurdle rate percentage (default 10.0%).
        margin_of_safety_target: Desired discount percentage from fair value (default 20.0%).

    Returns:
        A detailed investment determination report including PEG ratio, Graham intrinsic value,
        fair value estimate, upside/downside percentage, and a concrete rating.
    """
    clean_ticker = ticker.strip().upper()
    stock_data = get_stock(clean_ticker)
    if "error" in stock_data:
        return stock_data

    price = float(stock_data.get("current_price", 0))
    pe_ratio = float(stock_data.get("pe_ratio", 0))
    eps = float(stock_data.get("eps", 0))
    forward_pe = float(stock_data.get("forward_pe", pe_ratio))
    profit_margin = float(stock_data.get("profit_margin", 0))
    debt_to_equity = float(stock_data.get("debt_to_equity", 0))

    if price <= 0 or eps <= 0:
        return {"error": f"Invalid price (${price}) or EPS (${eps}) for calculating valuation on {clean_ticker}."}

    # PEG Ratio = (P/E) / (Growth Rate %)
    peg_ratio = round(pe_ratio / expected_growth_rate, 2) if expected_growth_rate > 0 else 0.0

    # Benjamin Graham Intrinsic Value formula: V = EPS * (8.5 + 2*g) * (4.4 / Y)
    # Using corporate bond yield proxy Y = 4.4 for normalized baseline
    graham_intrinsic_value = round(eps * (8.5 + 2 * expected_growth_rate), 2)

    # Simplified PE-based Fair Value estimate based on forward earnings & required return
    implied_fair_value = round(eps * (1 + (expected_growth_rate / 100)) * (expected_growth_rate * 1.5), 2)
    benchmark_fair_value = round((graham_intrinsic_value + implied_fair_value) / 2, 2)

    upside_percent = round(((benchmark_fair_value - price) / price) * 100, 2)
    buy_target_price = round(benchmark_fair_value * (1 - (margin_of_safety_target / 100)), 2)

    # Investment Determination Rating
    if peg_ratio <= 1.2 and upside_percent > margin_of_safety_target:
        verdict = "STRONG BUY / UNDERVALUED"
        rationale = f"PEG ratio ({peg_ratio}) is attractive and price offers a {upside_percent}% margin of safety over estimated fair value (${benchmark_fair_value})."
    elif peg_ratio <= 1.8 and upside_percent >= 0:
        verdict = "MODERATE BUY / FAIR VALUE"
        rationale = f"Trading near fair value (${benchmark_fair_value}). Good business quality with reasonable valuation."
    elif peg_ratio <= 2.5:
        verdict = "HOLD"
        rationale = f"Valuation is fully priced (PEG {peg_ratio}). Downside risk is moderate; hold existing positions."
    else:
        verdict = "CAUTION / OVERVALUED"
        rationale = f"High valuation multiple relative to growth rate (PEG {peg_ratio}). Trading at a premium to estimated fair value."

    return {
        "ticker": clean_ticker,
        "company_name": stock_data.get("company_name"),
        "current_price": price,
        "pe_ratio": pe_ratio,
        "forward_pe": forward_pe,
        "eps": eps,
        "profit_margin_pct": profit_margin,
        "debt_to_equity": debt_to_equity,
        "expected_growth_rate_pct": expected_growth_rate,
        "peg_ratio": peg_ratio,
        "graham_intrinsic_value": graham_intrinsic_value,
        "estimated_fair_value": benchmark_fair_value,
        "target_buy_price_with_safety_margin": buy_target_price,
        "upside_potential_pct": upside_percent,
        "verdict": verdict,
        "rationale": rationale,
    }


def fetch_market_history(ticker: str, period: str = "3mo") -> Dict[str, Any]:
    """Fetch live market price and historical trading performance for a ticker.

    Args:
        ticker: The stock ticker symbol (e.g. GOOGL, AAPL, NVDA, MSFT, AMZN).
        period: Historical period to fetch. Options: '1mo', '3mo', '6mo', '1y', '2y', '5y' (default '3mo').

    Returns:
        A dictionary containing current price, period return percentage, high, low,
        average volume, and recent price trend data.
    """
    clean_ticker = ticker.strip().upper()
    try:
        import yfinance as yf
        stock = yf.Ticker(clean_ticker)
        history = stock.history(period=period)

        if history.empty:
            return {"error": f"No historical market data found for ticker '{clean_ticker}'."}

        first_close = float(history["Close"].iloc[0])
        latest_close = float(history["Close"].iloc[-1])
        period_high = float(history["High"].max())
        period_low = float(history["Low"].min())
        avg_volume = int(history["Volume"].mean())
        total_return_pct = round(((latest_close - first_close) / first_close) * 100, 2)

        # 5 most recent closing data points for snapshot
        recent_trend = []
        for index, row in history.tail(5).iterrows():
            date_str = index.strftime("%Y-%m-%d") if hasattr(index, "strftime") else str(index)
            recent_trend.append({
                "date": date_str,
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        return {
            "ticker": clean_ticker,
            "period": period,
            "latest_price": round(latest_close, 2),
            "period_open_price": round(first_close, 2),
            "period_high": round(period_high, 2),
            "period_low": round(period_low, 2),
            "total_return_pct": total_return_pct,
            "average_daily_volume": avg_volume,
            "recent_closes": recent_trend,
        }
    except Exception as e:
        return {"error": f"Failed to retrieve market history for {clean_ticker}: {str(e)}"}


def fetch_live_stock_quote(ticker: str) -> Dict[str, Any]:
    """Fetch live real-time stock quote and market data from a free public finance API.

    Queries real-time market data (price, day change, 52-week high/low, currency, volume).
    Can be used with Finnhub (if FINNHUB_API_KEY environment variable is set) or
    direct Yahoo Finance public market endpoint without an API key.

    Args:
        ticker: The stock ticker symbol (e.g. AAPL, GOOGL, MSFT, NVDA).

    Returns:
        A dictionary containing the symbol, current live price, day change,
        percentage change, 52-week high/low, currency, and data source.
    """
    import json
    import os
    import urllib.parse
    import urllib.request

    clean_ticker = ticker.strip().upper()
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    # If Finnhub API key is present in environment, use Finnhub quote endpoint
    if finnhub_key:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={urllib.parse.quote(clean_ticker)}&token={finnhub_key}"
            req = urllib.request.Request(url, headers={"User-Agent": "StockScope/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("c", 0) > 0:
                    current_price = float(data["c"])
                    change = float(data.get("d", 0))
                    change_pct = float(data.get("dp", 0))
                    return {
                        "ticker": clean_ticker,
                        "current_price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2),
                        "high_of_day": round(float(data.get("h", 0)), 2),
                        "low_of_day": round(float(data.get("l", 0)), 2),
                        "open_of_day": round(float(data.get("o", 0)), 2),
                        "previous_close": round(float(data.get("pc", 0)), 2),
                        "source": "Finnhub API",
                    }
        except Exception:
            pass  # Fall through to Yahoo Finance public market API

    # Free public market endpoint (listed in public-apis Finance directory)
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(clean_ticker)}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            result = payload.get("chart", {}).get("result", [])
            if not result:
                return {"error": f"No market quote found for ticker '{clean_ticker}'."}
            meta = result[0].get("meta", {})
            current_price = float(meta.get("regularMarketPrice", 0))
            prev_close = float(meta.get("chartPreviousClose", current_price))
            change = round(current_price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

            return {
                "ticker": clean_ticker,
                "currency": meta.get("currency", "USD"),
                "exchange": meta.get("exchangeName", "Unknown"),
                "current_price": round(current_price, 2),
                "change": change,
                "change_percent": change_pct,
                "previous_close": round(prev_close, 2),
                "fifty_two_week_high": round(float(meta.get("fiftyTwoWeekHigh", 0)), 2),
                "fifty_two_week_low": round(float(meta.get("fiftyTwoWeekLow", 0)), 2),
                "regular_market_day_high": round(float(meta.get("regularMarketDayHigh", 0)), 2),
                "regular_market_day_low": round(float(meta.get("regularMarketDayLow", 0)), 2),
                "source": "Yahoo Finance Public API",
            }
    except Exception as e:
        return {"error": f"Failed to retrieve live quote for {clean_ticker}: {str(e)}"}


async def generate_memories_callback(callback_context: CallbackContext):
    """Save user preferences and facts to Memory Bank across sessions."""
    try:
        await callback_context.add_session_to_memory()
    except (ValueError, Exception):
        pass
    return None


instruction = INSTRUCTION

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        fetch_live_stock_quote,
        get_stock,
        list_stocks,
        save_stock,
        calculate_valuation_metrics,
        fetch_market_history,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)


