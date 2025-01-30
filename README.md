# Crypto Sentiment Analyzer 📊

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.20+-red.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A powerful cryptocurrency analysis tool that combines technical analysis with AI-powered sentiment analysis to provide comprehensive market insights. This project leverages advanced pattern recognition, market regime analysis, and sentiment indicators to help traders make informed decisions.

## 🚀 Features

### Technical Analysis
- **Pattern Recognition**: Automatically detect chart patterns (Head & Shoulders, Double Top/Bottom, etc.)
- **Support/Resistance Levels**: Dynamic calculation of key price levels
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR
- **Trend Analysis**: Advanced trend detection and strength measurement

### AI-Powered Sentiment Analysis
- **Market Sentiment Score**: Real-time sentiment analysis
- **Momentum Signals**: Identify market momentum and potential reversals
- **Volume Analysis**: Deep dive into trading volume patterns
- **Market Psychology**: Understand market participant behavior

### Market Regime Analysis
- **Trend Identification**: Automatic market phase detection
- **Volatility Analysis**: Risk assessment and volatility regime classification
- **Price Predictions**: AI-driven price movement forecasts
- **Risk Assessment**: Dynamic risk/reward ratio calculations

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/DeepCapital1/DeepCapital.git
cd DeepCapital
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🚀 Quick Start

1. Start the application:
```bash
streamlit run src/app.py
```

2. Open your browser and navigate to:
```
http://localhost:8501
```

3. Enter a cryptocurrency symbol (e.g., "BTC-USD") and start analyzing!

## 📊 Example Usage

```python
from pattern_detector import PatternDetector

# Initialize detector
detector = PatternDetector()

# Analyze Bitcoin
analysis = detector.analyze("BTC-USD")

# Get market insights
print(f"Market Regime: {analysis['market_regime']}")
print(f"Sentiment Score: {analysis['sentiment']['score']}")
print(f"Technical Patterns: {analysis['technical_patterns']}")
```

## 📚 Documentation

Comprehensive documentation is available in the `docs` folder:
- [API Documentation](./docs/api.md) - Detailed API reference
- [Setup Guide](./docs/setup.md) - Installation and configuration
- [Usage Guide](./docs/usage.md) - How to use the analyzer
- [Contributing Guidelines](./docs/CONTRIBUTING.md) - How to contribute

## 🔧 System Requirements

- Python 3.8+
- 4GB RAM (8GB recommended)
- Internet connection for real-time data
- OpenRouter API key for AI analysis

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./docs/CONTRIBUTING.md) for details on how to:
- Report bugs
- Suggest features
- Submit pull requests
- Set up development environment

## 📈 Performance

- Pattern detection: 2-5 seconds
- Sentiment analysis: Real-time
- Historical data: Varies by timeframe
- API rate limits: Managed automatically

## ⚠️ Important Notes

- This tool is for informational purposes only
- Always verify signals with multiple sources
- Past performance doesn't guarantee future results
- Use proper risk management

## 🔒 Security

- API keys are stored securely in `.env`
- No sensitive data is logged or stored
- Regular security updates
- Encrypted API communications

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for AI services
- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [Streamlit](https://streamlit.io/) for the web interface
- [pandas-ta](https://github.com/twopirllc/pandas-ta) for technical analysis

## 📧 Support

For support:
1. Check the [documentation](./docs/)
2. Review [common issues](./docs/setup.md#troubleshooting)
3. Open an [issue](https://github.com/DeepCapital1/DeepCapital/issues)

---
Made with ❤️ by DeepCapital 