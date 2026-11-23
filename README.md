# RealityCheck ⚡
> **Buy smarter. Not blindly.**  
> *Track 2: "One Smart Tool from Many Small Functions"*  
> **2nd Brain Labs × Geek Room Vibe-a-thon**

RealityCheck is an evidence-based AI purchasing intelligence assistant that helps users make informed purchasing decisions before spending money. By investigating product prices across marketplaces, detecting real discount potentials, analyzing genuine customer feedback and recurring complaints, discovering category alternatives, and comparing hardware specifications, RealityCheck generates a transparent 0–100 value score and a definitive recommendation: **BUY**, **WAIT**, or **AVOID**.

---

## 🏆 The Core Hackathon Objective (Track 2)

AI agents with access to a sprawling set of fine-grained tools suffer from **orchestration bloat**: high token overhead, multi-turn latency, fragility in sequencing, and parameter hallucination.

This project empirically compares two agent architectures:

| Architecture | Description | Tools Exposed | Tool Calls / Query |
| :--- | :--- | :--- | :--- |
| **Agent A (Many Small Tools)** | Exposes 7 individual granular functions. The agent must independently plan, invoke, validate, and chain tool inputs. | 7 tools (`search_product`, `compare_prices`, `find_discounts`, `analyze_reviews`, `find_alternatives`, `compare_specs`, `calculate_value_score`) | **7 calls** |
| **Agent B (One Smart Tool)** | Composed using **Synapse Custom mode** into one high-level Model Context Protocol (MCP) tool. Executes the workflow deterministically. | 1 tool (`investigate_purchase`) | **1 call (85.7% reduction)** |

---

## 🚀 Key Features

- **End-to-End Purchasing Investigation**: Answers queries like:
  > *"I'm considering buying Sony WH-CH720N headphones for ₹8,999. Are they worth it? Check pricing, reviews, alternatives, and value for money."*
- **Deterministic 0–100 Value Score**:
  - 🏷️ **Price Competitiveness**: 40% weight
  - 💬 **Review Sentiment**: 30% weight
  - ⚙️ **Specifications & Feature Balance**: 30% weight
- **BUY / WAIT / AVOID Verdict**: Evidence-backed recommendations with clear rationale and confidence metrics.
- **Synapse Custom Mode MCP Server**: Standards-compliant Model Context Protocol server exposing `investigate_purchase`.
- **Guarded Safety Architecture**: Demonstrates the `PREPARE -> DISPLAY -> USER CONFIRMATION -> EXECUTE` protocol for future actions (e.g. price drop alerts, wishlists). Blocks direct purchases by policy.
- **Interactive Streamlit Dashboard**: Full UI with product search, live agent benchmark comparison, workflow visualizer, and safety simulator.
- **Zero-Dependency Local Execution**: Includes an offline demo catalog with rich mock data across Headphones, Smartphones, Laptops, and Smartwatches. No paid API keys required to test!

---

## 🏗️ Architecture

```
                                  User Prompt
            "Is Sony WH-CH720N for ₹8,999 worth buying?"
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        ┌─────────────────────────┐           ┌─────────────────────────┐
        │  Agent A: 7 Small Tools │           │  Agent B: 1 Smart Tool  │
        └───────────┬─────────────┘           └───────────┬─────────────┘
                    │ (7 round-trips)                     │ (1 MCP invocation)
                    │                                     │
                    ▼                                     ▼
        ┌───────────────────────────────────────────────────────────────┐
        │                 Synapse Composed MCP Server                   │
        │             "investigate_purchase(product, price)"            │
        │                                                               │
        │  1. search_product()       ──▶ Disambiguate model name        │
        │  2. compare_prices()       ──▶ Benchmark marketplace low/avg  │
        │  3. find_discounts()       ──▶ Stacking & coupon evaluation   │
        │  4. analyze_reviews()      ──▶ Sentiment & recurring defects  │
        │  5. find_alternatives()    ──▶ Discover category peers        │
        │  6. compare_specs()        ──▶ Normalized attribute matrix    │
        │  7. calculate_value_score()──▶ 0-100 deterministic scoring    │
        │  8. Decision Matrix        ──▶ BUY / WAIT / AVOID verdict     │
        └───────────────────────────────┬───────────────────────────────┘
                                        │
                                        ▼
                             Structured JSON Report
                          + Streamlit Visual Dashboard
```

---

## 📁 Project Structure

```
realitycheck/
├── app.py                             # Streamlit interactive frontend
├── requirements.txt                   # Python dependencies
├── README.md                          # Documentation and setup guide
├── .env.example                       # Environment template
├── .gitignore                         # Git exclusion rules
│
├── data/
│   └── products.json                  # Labeled mock catalog (12+ items)
│
├── src/
│   ├── __init__.py
│   ├── schemas.py                     # Pydantic data schemas
│   ├── product_search.py              # Function 1: Fuzzy catalog lookup
│   ├── price_analysis.py              # Function 2: Marketplace comparison
│   ├── discount_analysis.py           # Function 3: Coupon & bank discount engine
│   ├── review_analysis.py             # Function 4: Customer sentiment analyzer
│   ├── alternatives.py                # Function 5: Category peer discovery
│   ├── spec_comparison.py             # Function 6: Hardware spec matrix
│   ├── value_scoring.py               # Function 7: Deterministic 0-100 scoring
│   ├── purchase_workflow.py           # Composed investigate_purchase pipeline
│   └── safety.py                      # Guarded confirmation architecture
│
├── agents/
│   ├── __init__.py
│   ├── many_tools_agent.py            # Agent A (7 fine-grained tools)
│   └── smart_tool_agent.py            # Agent B (1 Synapse composed tool)
│
├── synapse/
│   ├── __init__.py
│   ├── investigate_purchase_server.py # MCP STDIO Server for Synapse
│   ├── synapse_config.json            # Synapse Custom mode specification
│   └── synapse_bridge.py              # Synapse runtime & CLI detector
│
├── evaluation/
│   ├── __init__.py
│   ├── benchmark.py                   # Automated comparative benchmark
│   └── test_cases.json                # 5 standardized test scenarios
│
└── tests/
    ├── test_individual_functions.py   # Tests for search, discounts, specs, score
    ├── test_price_analysis.py         # Tests for price comparison & tiers
    ├── test_review_analysis.py        # Tests for sentiment & empty reviews
    ├── test_purchase_workflow.py      # Tests for composed pipeline resilience
    ├── test_safety.py                 # Tests for confirmation guardrails
    └── test_benchmark_and_agents.py   # Tests for Agent A, Agent B & benchmark
```

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
- Python 3.11+
- Node.js (for `npx @2ndbrainlabs-ai/synapse-cli` inspection, optional)

### 2. Clone and Setup Environment
```bash
git clone <repository_url>
cd SVG
```

Create a virtual environment (optional but recommended):
```bash
py -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

Install dependencies:
```bash
py -m pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
```bash
cp .env.example .env
```
*Note: RealityCheck is designed to work completely offline out of the box with built-in mock orchestrators. No paid API keys are required to run tests, execute benchmarks, or use the Streamlit interface!*

---

## 🖥️ Running the Application

Launch the Streamlit interactive dashboard:
```bash
py -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Streamlit Pages:
1. **🔍 Product Investigation**: Test any product (e.g. *Sony WH-CH720N* at ₹8,999) using Agent A or Agent B. See value score breakdown, price comparison, discounts, sentiment, spec matrix, and verdict.
2. **⚖️ Agent Comparison & Benchmark**: Run live benchmarks across all 5 test scenarios and view side-by-side latency, tool call reductions, and consistency charts.
3. **⚡ Workflow & Synapse Engine**: Interactive step-by-step visualizer of the 8 pipeline stages and Synapse Custom mode architecture.
4. **🛡️ Safety & Guardrails**: Test the `PREPARE -> CONFIRM -> EXECUTE` safety workflow for price alerts and wishlists.

---

## 📊 Running the Benchmark

Run the automated empirical benchmark from the command line:
```bash
py evaluation/benchmark.py
```

### Actual Measured Results:
```
================================================================================
 RealityCheck Hackathon Track 2 Benchmark: Many Tools vs. One Smart Tool
================================================================================
Scenarios Evaluated: 5 | Mode: ACTUAL_MEASURED
--------------------------------------------------------------------------------
Metric                              | Agent A (Many Tools) | Agent B (One Smart Tool)
--------------------------------------------------------------------------------
Total Tool Invocations              | 35                   | 5                   
Avg Tool Invocations / Run          | 7.0                  | 1.0                 
Average Latency (ms)                | 2.47                 | 1.73                
Failed Tool Calls                   | 0                    | 0                   
Workflow Completion Rate            | 100.0%               | 100.0%               
--------------------------------------------------------------------------------
Tool Call Complexity Reduction : 85.7% fewer tool calls
Recommendation Consistency     : 100.0% exact agreement
================================================================================
```

---

## 🧩 Synapse Custom Mode Integration

Synapse from **2nd Brain Labs** is used to generate the high-level composed MCP server.

### Synapse CLI Usage:
1. Initialize Synapse in the project:
   ```bash
   npx @2ndbrainlabs-ai/synapse-cli init
   ```
2. Build the MCP server using Custom mode:
   ```bash
   npx @2ndbrainlabs-ai/synapse-cli build --custom -q "investigate product purchase"
   ```
3. Run the composed MCP server over STDIO:
   ```bash
   py synapse/investigate_purchase_server.py
   ```

*Credentials notice*: If using hosted Synapse cloud features, supply your `SYNAPSE_API_KEY` obtained from [synapse.2ndbrainlabs.ai](https://synapse.2ndbrainlabs.ai). In local mode, the included FastMCP/MCPServer runner (`synapse/investigate_purchase_server.py`) operates stand-alone.

---

## 🧪 Running Automated Tests

RealityCheck includes a comprehensive pytest suite covering all 7 functions, the composed workflow, resilience guards, edge cases, safety confirmation, and agents:

```bash
py -m pytest tests/ -v
```

All 21 test cases pass with 100% success rate.

---

## 🛡️ Safety & Confirmation Architecture

RealityCheck enforces a strict safety protocol for data-modifying actions:
1. **PREPARE**: Action is registered and a human-readable confirmation card is generated.
2. **DISPLAY**: The user is shown the exact parameters (product, price threshold, action type).
3. **USER CONFIRMATION**: Explicit user consent is required. If declined, execution is halted immediately.
4. **EXECUTE**: Only confirmed actions execute.
*Policy Guard*: Direct autonomous purchases, payment processing, or scraping are permanently blocked in this MVP.

---

## ⚠️ Limitations & Mock Data Notice

- **Mock Data**: Products, prices, discounts, and reviews in `data/products.json` are curated sample data for hackathon demonstration. They do not represent real-time live e-commerce prices.
- **No Autonomous Purchasing**: The system provides purchasing intelligence and decision guidance; it does not complete checkout or access financial accounts.

---

## 🗺️ Future Roadmap

- [ ] Connect live retailer APIs (Amazon Product Advertising API, Flipkart Affiliate API).
- [ ] OCR receipt analysis and warranty receipt tracking.
- [ ] Personalized budget and monthly spending constraint modeling.
- [ ] Synapse remote cloud deployment with OAuth 2.0 consumer authentication.
