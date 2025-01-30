# Crypto Sentiment Analyzer API Documentation

## Overview
This document provides detailed information about the APIs available in the Crypto Sentiment Analyzer project. The project consists of two main components: Pattern Detection and Sentiment Analysis.

## Pattern Detector API

### Class: PatternDetector

The `PatternDetector` class provides comprehensive technical analysis functionality using AI-powered pattern recognition.

#### Initialization
```python
detector = PatternDetector()
```
Requires:
- `OPENROUTER_API_KEY` in environment variables

#### Public Methods

##### 1. fetch_data(symbol, interval='1d', period='6mo')
Fetches historical price data for a given symbol.

**Parameters:**
- `symbol` (str): Trading symbol (e.g., "BTC-USD")
- `interval` (str): Time interval ('1d', '1h', '15m', '5m')
- `period` (str): Historical period ('1mo', '3mo', '6mo', '1y')

**Returns:**
- `pandas.DataFrame`: Historical price data with OHLCV columns

##### 2. add_technical_indicators(df)
Adds technical indicators to the price data.

**Parameters:**
- `df` (pandas.DataFrame): Price data with OHLCV columns

**Returns:**
- `pandas.DataFrame`: Enhanced dataframe with technical indicators:
  - RSI (14 periods)
  - MACD (12, 26, 9)
  - Bollinger Bands (20, 2)
  - ATR (14 periods)
  - Returns and Volatility

##### 3. detect_patterns(df, lookback=30)
Performs comprehensive pattern detection and analysis.

**Parameters:**
- `df` (pandas.DataFrame): Price data with technical indicators
- `lookback` (int): Number of periods to analyze

**Returns:**
```python
{
    'patterns': str,  # JSON string of detected patterns
    'market_regime': str,  # JSON string of market regime analysis
    'price_prediction': str,  # JSON string of price predictions
    'support_resistance': str,  # JSON string of support/resistance levels
    'timestamp': str  # ISO format timestamp
}
```

##### 4. plot_pattern(df, pattern_info)
Creates an interactive plot with pattern annotations.

**Parameters:**
- `df` (pandas.DataFrame): Price data with technical indicators
- `pattern_info` (dict): Pattern analysis results

**Returns:**
- `plotly.graph_objects.Figure`: Interactive chart with patterns and indicators

##### 5. analyze(symbol, timeframe='1d', period='3mo')
Performs comprehensive market analysis.

**Parameters:**
- `symbol` (str): Trading symbol
- `timeframe` (str): Time interval
- `period` (str): Analysis period

**Returns:**
```python
{
    'symbol': str,
    'timestamp': str,
    'current_price': float,
    'technical_patterns': {
        'detected_patterns': list,
        'quality_score': int,
        'reliability': str
    },
    'market_regime': {
        'regime': str,
        'confidence': int,
        'trend_strength': int,
        'volatility_regime': str,
        'characteristics': list
    },
    'sentiment': {
        'overall': str,
        'score': int,
        'momentum_signals': list,
        'reversal_signals': list,
        'volume_analysis': str,
        'market_psychology': str
    },
    'market_context': {
        'phase': str,
        'dominant_traders': str,
        'volume_profile': str,
        'volatility_state': str,
        'risk_reward_ratio': float,
        'position_sizing': str,
        'key_levels': dict,
        'scenarios': list
    },
    'technical_indicators': {
        'rsi': float,
        'macd': float,
        'macd_signal': float,
        'volatility': float,
        'atr': float
    }
}
```

## Response Formats

### Pattern Analysis Response
```json
{
    "patterns": ["string"],
    "quality_score": 0,
    "completion": 0,
    "reliability": "string",
    "price_targets": [0],
    "key_levels": [0]
}
```

### Market Regime Response
```json
{
    "regime": "string",
    "confidence": 0,
    "characteristics": ["string"],
    "trend_strength": 0,
    "volatility_regime": "string"
}
```

### Sentiment Analysis Response
```json
{
    "overall_sentiment": "string",
    "sentiment_score": 0,
    "momentum_signals": ["string"],
    "reversal_signals": ["string"],
    "volume_analysis": "string",
    "strength_indicators": ["string"],
    "weakness_indicators": ["string"],
    "market_psychology": "string"
}
```

## Error Handling

All methods include comprehensive error handling and return appropriate error responses:

- API errors return JSON with error details
- Data fetching errors return None
- Analysis errors return default values with error indicators
- All errors are logged with detailed messages

## Dependencies

Required Python packages:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `yfinance`: Yahoo Finance data fetching
- `pandas_ta`: Technical analysis indicators
- `plotly`: Interactive plotting
- `requests`: HTTP requests
- `python-dotenv`: Environment variable management
- `scikit-learn`: Machine learning utilities

## Environment Variables

Required environment variables:
- `OPENROUTER_API_KEY`: API key for DeepSeek AI services

## Usage Example

```python
from pattern_detector import PatternDetector

# Initialize detector
detector = PatternDetector()

# Fetch and analyze data
symbol = "BTC-USD"
df = detector.fetch_data(symbol)
df = detector.add_technical_indicators(df)
analysis = detector.detect_patterns(df)

# Generate plot
fig = detector.plot_pattern(df, analysis)
fig.show()

# Get comprehensive analysis
full_analysis, data = detector.analyze(symbol)
```

## Rate Limits and Performance

- API calls are rate-limited by the OpenRouter service
- Recommended to cache results for frequently analyzed symbols
- Technical indicator calculations are optimized for performance
- Pattern detection typically takes 2-5 seconds per analysis
- Historical data fetching depends on the period requested

## Best Practices

1. **Error Handling**
   - Always check for None returns from `fetch_data()`
   - Validate DataFrame contents before analysis
   - Handle API timeouts and connection errors

2. **Data Management**
   - Cache frequently used data
   - Use appropriate timeframes for analysis
   - Clean and validate data before processing

3. **Performance Optimization**
   - Limit lookback periods for large datasets
   - Use appropriate technical indicator periods
   - Cache API responses when possible

## Related Documentation

- [Setup Guide](./docs/setup.md) - Installation and configuration instructions
- [Usage Guide](./docs/usage.md) - Detailed usage instructions and examples
- [Contributing Guidelines](./docs/CONTRIBUTING.md) - How to contribute to the project

## Support

For API support and issues:
- Check the error logs for detailed messages
- Verify API key and environment variables
- Ensure all dependencies are correctly installed
- Contact support for API-specific issues
