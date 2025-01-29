# 📈 Technical Analysis Pattern Detector

An advanced technical analysis tool that uses DeepSeek AI to identify complex chart patterns and provide detailed market insights.

## 🌟 Features

- AI-powered pattern recognition for complex chart formations
- Real-time technical analysis with multiple timeframes
- Comprehensive pattern analysis including:
  - Pattern identification and reliability scoring
  - Support and resistance levels
  - Entry and exit points
  - Risk assessment
  - Price targets
  - Historical success rates
- Interactive charts with technical indicators
- Multiple timeframe analysis (5m, 15m, 1h, 1d)
- Support for crypto and traditional markets

## 🔧 Technical Indicators

- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Bollinger Bands
- Average True Range (ATR)
- Price volatility metrics
- Custom engagement-weighted analysis

## 🛠️ Setup Instructions

1. Clone the repository:
```bash
git clone <your-repo-url>
cd technical_analysis
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

5. Run the application:
```bash
cd src
streamlit run app.py
```

## 📊 Usage Guide

1. Enter a trading symbol (e.g., BTC-USD, ETH-USD, AAPL)
2. Select your preferred timeframe (5m, 15m, 1h, 1d)
3. Choose the analysis period (1mo, 3mo, 6mo, 1y)
4. Click "Analyze Pattern" to get:
   - Interactive price chart with patterns
   - Detailed pattern analysis
   - Support and resistance levels
   - Entry/exit suggestions
   - Risk assessment
   - Technical indicators

## 🔍 Pattern Recognition

The tool identifies various chart patterns including:
- Head and Shoulders
- Double Top/Bottom
- Triangle Patterns
- Flag Patterns
- Channel Patterns
- Cup and Handle
- Wedge Formations
- And more...

## ⚙️ Customization

### Adjusting Technical Indicators

You can modify indicator parameters in `pattern_detector.py`:
```python
self.indicators = {
    'RSI': {'timeperiod': 14},  # Adjust RSI period
    'MACD': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},  # Adjust MACD parameters
    'BB': {'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2},  # Adjust Bollinger Bands
    'ATR': {'timeperiod': 14}  # Adjust ATR period
}
```

### Pattern Detection Settings

Modify the lookback period and analysis parameters:
```python
# In pattern_detector.py
def detect_patterns(self, df, lookback=30):  # Adjust lookback period
```

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Always conduct your own research and consider consulting with a financial advisor before making investment decisions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 