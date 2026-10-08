# StockScope AI (Stock Monitoring & Investment Intelligence Assistant)

A conversational AI agent built with Google Agent Development Kit (ADK) that helps individual investors evaluate stock investments by monitoring watchlists, retrieving real-time quotes, analyzing historical performance & valuation metrics (P/E ratio, EPS, margins, market cap), and generating structured A2UI visual cards.

## 🎥 Demo Video

> Demo video: [`assets/nvda_1066c49d.mp4`](assets/nvda_1066c49d.mp4)

---

## 🌟 Key Features & Tools

- **Real-Time Live Stock Quotes**: Integrates public market endpoints (Finnhub API / Yahoo Finance) via `fetch_live_stock_quote` to fetch live stock prices, percentage change, and 52-week ranges.
- **Stock Fundamentals & Valuation**: Retrieval of key investment metrics including P/E ratios, EPS, debt-to-equity, and profit margins.
- **Historical Performance Analysis**: `fetch_market_history` inspects multi-period price history and movement trends.
- **Persistent Long-Term Memory**: Vertex AI Memory Bank and Firestore integration remember user watchlists, portfolio preferences, and investment goals across sessions.
- **Rich A2UI Visual Cards**: Formats stock summaries, watchlist snapshots, and financial metrics as structured A2UI cards.

---

## 🏗️ Project Structure

```
stockscope-agent/
├── app/
│   ├── agent.py                 # Core ADK agent definition & tools
│   ├── fast_api_app.py          # FastAPI backend server with A2A protocol
│   ├── prompt.py                # A2UI-optimized system prompt
│   ├── a2ui_utils.py            # A2UI message wrapper callback
│   └── app_utils/               # Services, memory, and A2A handlers
├── assets/
│   └── nvda_1066c49d.mp4        # Agent demonstration video
├── frontend/                    # Web chat interface
├── tests/                       # Unit & integration test suites
├── project_brief.md             # Project design and tool coverage brief
├── agents-cli-manifest.yaml     # Agent deployment specification
└── pyproject.toml               # Python project configuration & dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 - 3.13
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud SDK (`gcloud`)

### Installation

```bash
# Clone the repository
git clone https://github.com/jameslin14/buildwithgemini-stockscope-agent.git
cd buildwithgemini-stockscope-agent

# Install dependencies
uv sync
```

### Running Locally

Launch the ADK Web playground:

```bash
uv run adk web --port 8080 --allow_origins "*" --reload_agents
```

Open `http://localhost:8080` in your browser. (Turn off Token Streaming in the UI settings for optimal A2UI card rendering.)

---

## ☁️ Deployment

Deploy to Vertex AI Agent Runtime:

```bash
agents-cli deploy --region us-east1
```
