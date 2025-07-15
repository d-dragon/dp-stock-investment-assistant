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

Copy `config/config_example.yaml` to `config/config.yaml` and fill in your API keys and AI model parameters.

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
