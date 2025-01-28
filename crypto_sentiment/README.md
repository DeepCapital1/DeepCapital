# 🚀 Crypto Sentiment Analyzer

A powerful cryptocurrency sentiment analysis tool that uses DeepSeek's advanced AI to analyze social media sentiment and provide comprehensive market insights.

## 🌟 Features

- Real-time Twitter data analysis for any cryptocurrency ticker
- Advanced sentiment analysis using DeepSeek's AI
- Comprehensive market analysis including:
  - Overall market sentiment & confidence level
  - Key factors driving sentiment
  - Potential price impact analysis
  - Risk factors
  - Short-term outlook (24-48 hours)
- Detailed individual tweet analysis
- Engagement-weighted sentiment scoring
- Interactive web interface built with Streamlit

## 🛠️ Setup Instructions

1. Clone the repository:
```bash
git clone <your-repo-url>
cd crypto_sentiment
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

## 🔧 Configuration & Customization

### Adjusting Tweet Collection

You can modify the following parameters in `data_collector.py`:
- `MAX_TWEETS`: Change the maximum number of tweets to collect (default: 100)
- `SCROLL_PAUSE_TIME`: Adjust the pause time between scrolls (default: 1 second)
- `MAX_SCROLL_ATTEMPTS`: Modify the maximum number of scroll attempts (default: 10)

Example:
```python
# In data_collector.py
MAX_TWEETS = 200  # Increase to collect more tweets
SCROLL_PAUSE_TIME = 0.5  # Decrease for faster collection
MAX_SCROLL_ATTEMPTS = 20  # Increase for more thorough collection
```

### Customizing Analysis

The sentiment analyzer can be customized in `sentiment_analyzer.py`:
- Adjust the sentiment analysis prompt
- Modify the weight calculation for engagement scores
- Customize the analysis sections and format

## 📊 Usage Examples

1. **Basic Ticker Analysis**:
   - Enter a crypto ticker (e.g., $BTC, $ETH)
   - Select the number of hours of historical data (1-72 hours)
   - Click "Analyze Ticker"

2. **Single Text Analysis**:
   - Input any crypto-related text
   - Get detailed sentiment analysis with step-by-step reasoning

3. **Multiple Sources Analysis**:
   - Analyze up to 10 different text sources simultaneously
   - Get aggregated sentiment metrics and individual analyses

## 🔍 Advanced Features

### Engagement Weighting
The analyzer uses tweet engagement metrics (likes, retweets, etc.) to weight the sentiment scores. Higher engagement tweets have more influence on the final sentiment score.

### Sentiment Range
The tool provides sentiment scores from -1 (very negative) to 1 (very positive), with detailed breakdowns of:
- Overall weighted sentiment
- Individual tweet sentiments
- Sentiment distribution and range

### Analysis Customization
Users can adjust the analysis timeframe from 1 to 72 hours of historical data to get different perspectives on market sentiment.

## ⚠️ Limitations

- Twitter data collection is rate-limited
- Analysis time increases with the number of tweets
- Requires active internet connection
- API key rate limits apply

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 