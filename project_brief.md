# My agent: StockScope AI (Stock Monitoring & Investment Intelligence Assistant)
One-liner: A conversational agent that helps individual investors evaluate stock investments by monitoring watchlists, retrieving historical performance and valuation metrics (P/E ratio, EPS, margins, market cap), and computing financial valuation models.

Tool coverage:
- Memory: User's stock watchlist, portfolio holdings, preferred valuation criteria (e.g. target P/E thresholds, dividend preference, risk tolerance), and past analysis notes.
- Tools: 
  - Stock quote & company fundamental lookup (P/E ratio, forward P/E, EPS, market cap, dividend yield, debt-to-equity, profit margins).
  - Historical price & performance retrieval (52-week high/low, multi-year price history and growth trends).
  - Financial news & earnings summary retrieval.
- Catalog/UI: Watchlist snapshot cards, fundamental metric comparison tables across peer companies, and financial health scorecards rendered with A2UI.
- Image gen: Infographic-style company comparison cards, sector breakdown visuals, and visual report summary badges.
- Sandbox: Financial valuation models (DCF - Discounted Cash Flow calculations, Graham number, historical return CAGR, risk/volatility analysis).

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for running valuation & DCF models; external financial data API (or Firestore mock market DB) for quotes and financial ratios.
