# DP Stock-Investment Assistant

An AI-powered assistant for stock investment analysts, leveraging OpenAI's GPT API to provide market insights, answer financial queries, and analyze stock data.

## Features

- **Natural Language Q&A:** Ask questions about stocks, market trends, or financial reports.
- **Stock Data Analysis:** Integrate with financial APIs to analyze historical and real-time data.
- **Earnings Summaries:** Summarize key points from earnings releases and news.
- **Portfolio Suggestions:** Get AI-generated investment ideas and portfolio optimizations.
- **Import Stock Data:** Easily import stock data from various sources for analysis.
- **AI Model Configuration:** Set custom parameters and configuration options for AI models to tailor analysis and recommendations.
- **Set Analyzing Targets/Goals:** Define specific stocks, sectors, or financial metrics to focus analysis on your investment objectives.
- **Export Report:** Generate and export analysis reports in formats such as PDF, CSV, or markdown for sharing and documentation.

## Getting Started

### Prerequisites

- Python 3.8+
- [OpenAI API key](https://platform.openai.com/)
- (Optional) Financial data API keys (e.g., Yahoo Finance, Alpha Vantage)

### Installation

```bash
git clone https://github.com/d-dragon/dp-stock-investment-assistant.git
cd dp-stock-investment-assistant
pip install -r requirements.txt
```

### Configuration

There are two ways to configure the application:

#### Method 1: Using YAML Configuration File

1. Copy `config/config_example.yaml` to `config/config.yaml`
2. Fill in your API keys and customize settings in the YAML file

#### Method 2: Using Environment Variables (Recommended)

1. Copy `.env.example` to `.env`
2. Fill in your environment variables in the `.env` file

```bash
# Copy the example files
copy config\config_example.yaml config\config.yaml  # Windows
copy .env.example .env                               # Windows

# OR on Unix/macOS:
# cp config/config_example.yaml config/config.yaml
# cp .env.example .env
```

The application supports environment variable overrides, which means:

- Values in `.env` will override corresponding values in `config.yaml`
- System environment variables will override `.env` values
- This provides flexibility for different deployment environments

#### Required Environment Variables

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

#### Optional Environment Variables

```bash
# OpenAI Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Financial APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
ALPHA_VANTAGE_ENABLED=false
YAHOO_FINANCE_ENABLED=true

# Application Settings
APP_LOG_LEVEL=INFO
APP_CACHE_ENABLED=true
APP_MAX_HISTORY=100
```

See `.env.example` for a complete list of available environment variables.

### Usage

Run the main agent:

```bash
python src/main.py
```

## Roadmap

- [ ] Basic GPT-powered Q&A
- [ ] Stock data integration
- [ ] Report summarization
- [ ] Portfolio suggestion engine
- [ ] Stock data import feature
- [ ] AI model configuration interface
- [ ] Set analysis targets/goals
- [ ] Export report feature

---

## License

MIT
