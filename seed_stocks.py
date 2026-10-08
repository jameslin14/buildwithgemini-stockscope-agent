"""Seed script to populate initial stock data in Firestore."""
from google.cloud import firestore

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-c7f7b6dbf6e7"

SEED_STOCKS = [
    {
        "ticker": "GOOGL",
        "company_name": "Alphabet Inc.",
        "sector": "Communication Services",
        "current_price": 182.50,
        "pe_ratio": 24.8,
        "forward_pe": 21.2,
        "eps": 7.36,
        "market_cap": "2.25T",
        "dividend_yield": 0.45,
        "profit_margin": 27.5,
        "debt_to_equity": 0.11,
        "fifty_two_week_high": 191.75,
        "fifty_two_week_low": 129.01,
        "analysis_notes": "Strong search dominance, cloud growth accelerating, aggressive AI infrastructure investment.",
    },
    {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "current_price": 228.10,
        "pe_ratio": 33.2,
        "forward_pe": 29.5,
        "eps": 6.87,
        "market_cap": "3.48T",
        "dividend_yield": 0.44,
        "profit_margin": 26.3,
        "debt_to_equity": 1.45,
        "fifty_two_week_high": 237.23,
        "fifty_two_week_low": 164.08,
        "analysis_notes": "High recurring services revenue and massive cash flow; valuation premium reflects ecosystem lock-in.",
    },
    {
        "ticker": "NVDA",
        "company_name": "NVIDIA Corporation",
        "sector": "Technology",
        "current_price": 125.40,
        "pe_ratio": 48.5,
        "forward_pe": 34.0,
        "eps": 2.58,
        "market_cap": "3.08T",
        "dividend_yield": 0.03,
        "profit_margin": 55.0,
        "debt_to_equity": 0.17,
        "fifty_two_week_high": 140.76,
        "fifty_two_week_low": 40.85,
        "analysis_notes": "Leading AI accelerator market share; high margins, but sensitive to data center capex cycles.",
    },
    {
        "ticker": "MSFT",
        "company_name": "Microsoft Corporation",
        "sector": "Technology",
        "current_price": 418.00,
        "pe_ratio": 34.1,
        "forward_pe": 28.9,
        "eps": 12.25,
        "market_cap": "3.11T",
        "dividend_yield": 0.72,
        "profit_margin": 36.1,
        "debt_to_equity": 0.42,
        "fifty_two_week_high": 468.35,
        "fifty_two_week_low": 327.00,
        "analysis_notes": "Diverse revenue across Azure enterprise cloud, Office 365, and gaming; strong balance sheet.",
    },
    {
        "ticker": "AMZN",
        "company_name": "Amazon.com, Inc.",
        "sector": "Consumer Cyclical",
        "current_price": 186.20,
        "pe_ratio": 41.6,
        "forward_pe": 32.5,
        "eps": 4.47,
        "market_cap": "1.94T",
        "dividend_yield": 0.0,
        "profit_margin": 8.2,
        "debt_to_equity": 0.58,
        "fifty_two_week_high": 201.20,
        "fifty_two_week_low": 118.35,
        "analysis_notes": "AWS cloud profit engine plus expanding retail advertising and fulfillment efficiency margins.",
    },
]


def seed():
    print(f"Connecting to Firestore using project ID: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("stocks")

    for stock in SEED_STOCKS:
        doc_id = stock["ticker"]
        collection_ref.document(doc_id).set(stock)
        print(f"✓ Seeded stock: {doc_id} ({stock['company_name']})")

    print("Done seeding Firestore!")


if __name__ == "__main__":
    seed()
