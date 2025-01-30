# Crypto Sentiment Analyzer Usage Guide

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Features](#features)
- [User Interface](#user-interface)
- [Analysis Types](#analysis-types)
- [Interpreting Results](#interpreting-results)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The Crypto Sentiment Analyzer is a powerful tool that combines technical analysis with AI-powered sentiment analysis to provide comprehensive market insights. This guide will help you understand how to use the application effectively.

## Getting Started

### Basic Usage
1. Launch the application:
   ```bash
   streamlit run src/app.py
   ```
2. Open your browser to `http://localhost:8501`
3. Enter a crypto symbol (e.g., "BTC-USD", "ETH-USD")
4. Select analysis parameters
5. Click "Analyze" to start

### Quick Start Example
```python
# Example using the API directly
from pattern_detector import PatternDetector

detector = PatternDetector()
analysis = detector.analyze("BTC-USD")
print(analysis['market_regime'])
```

## Features

### 1. Technical Analysis
- Pattern Detection
  - Support/Resistance levels
  - Chart patterns (Head & Shoulders, Double Top/Bottom, etc.)
  - Trend lines and channels
  
- Technical Indicators
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - ATR (Average True Range)

### 2. Sentiment Analysis
- Market Sentiment Score
- Momentum Signals
- Reversal Indicators
- Volume Analysis
- Market Psychology Assessment

### 3. Market Regime Analysis
- Trend Identification
- Volatility Analysis
- Market Phase Detection
- Risk Assessment

## User Interface

### Main Dashboard
- **Symbol Input**: Enter cryptocurrency trading pair
- **Timeframe Selection**: Choose analysis period
  - Options: 1d, 1h, 15m, 5m
- **Period Selection**: Historical data range
  - Options: 1mo, 3mo, 6mo, 1y

### Analysis Panel
- **Technical Chart**: Interactive price chart with indicators
- **Pattern Overlay**: Visual pattern identification
- **Sentiment Dashboard**: Real-time sentiment metrics
- **Market Context**: Current market regime and analysis

### Settings
- **Indicator Parameters**: Customize technical indicators
- **Display Options**: Chart customization
- **Analysis Depth**: Configure analysis detail level

## Analysis Types

### 1. Quick Analysis
```
Purpose: Rapid market overview
Timeframe: 1h or less
Best for: Day trading, quick decisions
```

### 2. Deep Analysis
```
Purpose: Comprehensive market study
Timeframe: 1d or more
Best for: Position trading, trend following
```

### 3. Custom Analysis
```
Purpose: Specific pattern or indicator focus
Timeframe: User-defined
Best for: Strategy development, backtesting
```

## Interpreting Results

### Technical Patterns
- **Strong Patterns**: Score > 80
  - High reliability
  - Clear price targets
  - Multiple confirmations

- **Moderate Patterns**: Score 50-80
  - Potential opportunities
  - Requires additional confirmation
  - Monitor for development

- **Weak Patterns**: Score < 50
  - Low reliability
  - Use as supporting evidence only
  - Requires strong confirmation

### Sentiment Indicators
```json
{
    "Bullish": "Score > 60, Strong buying pressure",
    "Neutral": "Score 40-60, Consolidation phase",
    "Bearish": "Score < 40, Strong selling pressure"
}
```

### Market Regimes
1. **Trending Market**
   - Strong directional movement
   - Clear support/resistance levels
   - High momentum indicators

2. **Ranging Market**
   - Sideways price action
   - Clear trading range
   - Low momentum indicators

3. **Volatile Market**
   - Large price swings
   - Breakout potential
   - High risk/reward opportunities

## Advanced Usage

### 1. Custom Indicators
```python
# Add custom technical indicators
def custom_indicator(data):
    # Your indicator logic here
    return indicator_values

# Apply to analysis
detector.add_custom_indicator(custom_indicator)
```

### 2. Pattern Detection Sensitivity
```python
# Adjust pattern detection parameters
detector.detect_patterns(
    lookback=30,
    sensitivity=0.7,
    confirmation_threshold=0.8
)
```

### 3. Automated Analysis
```python
# Schedule regular analysis
import schedule
import time

def automated_analysis():
    detector = PatternDetector()
    analysis = detector.analyze("BTC-USD")
    # Process results

schedule.every(1).hour.do(automated_analysis)
```

## Best Practices

### 1. Analysis Workflow
1. Start with longer timeframes
2. Identify major trends
3. Zoom into shorter timeframes
4. Confirm patterns with multiple indicators
5. Consider sentiment context

### 2. Risk Management
- Use stop-loss orders
- Consider position sizing
- Monitor market volatility
- Diversify analysis methods

### 3. Performance Optimization
- Cache frequent analyses
- Use appropriate timeframes
- Limit API calls
- Monitor system resources

## Examples

### 1. Trend Following Strategy
```python
# Example of trend following analysis
analysis = detector.analyze("BTC-USD", timeframe="1d")
if analysis['market_regime']['trend_strength'] > 0.7:
    if analysis['sentiment']['overall'] == "bullish":
        print("Strong bullish trend confirmed")
```

### 2. Pattern Trading Setup
```python
# Example of pattern-based trading setup
patterns = detector.detect_patterns(data)
for pattern in patterns:
    if pattern['quality_score'] > 80:
        print(f"High-quality {pattern['name']} detected")
        print(f"Target: {pattern['price_targets']}")
```

### 3. Sentiment-Based Analysis
```python
# Example of sentiment-driven analysis
sentiment = detector.analyze_sentiment()
if sentiment['score'] > 70 and sentiment['momentum_signals']:
    print("Strong positive sentiment with momentum")
```

## Tips and Tricks

1. **Pattern Confirmation**
   - Use multiple timeframes
   - Combine technical and sentiment signals
   - Wait for pattern completion

2. **Performance Optimization**
   - Cache frequently used data
   - Use appropriate analysis periods
   - Optimize API calls

3. **Risk Management**
   - Set clear entry/exit points
   - Use appropriate position sizing
   - Monitor market conditions

## Troubleshooting Common Issues

### 1. Analysis Errors
```
Issue: No patterns detected
Solution: Adjust lookback period or sensitivity
```

### 2. Performance Issues
```
Issue: Slow analysis
Solution: Reduce data period or cache results
```

### 3. Data Quality
```
Issue: Incomplete patterns
Solution: Verify data source and timeframe
```

## Updates and Maintenance

- Check for regular updates
- Monitor API usage
- Review analysis performance
- Update configuration as needed

For more detailed information, refer to:
- [API Documentation](./docs/api.md)    
- [Setup Guide](./docs/setup.md)
- [Contributing Guidelines](./docs/CONTRIBUTING.md)
