import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import pandas_ta as ta
from dotenv import load_dotenv
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

class PatternDetector:
    def __init__(self):
        print("\n=== Initializing Pattern Detector ===")
        load_dotenv()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            print("❌ Error: OpenRouter API key not found!")
            raise ValueError("OpenRouter API key not found in environment variables")
        else:
            print("✅ API Key loaded successfully")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8501',
            'X-Title': 'Technical Analysis Pattern Detector'
        }
        print("✅ Headers configured")
        
        # Initialize technical indicators
        self.indicators = {
            'RSI': {'timeperiod': 14},
            'MACD': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
            'BB': {'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2},
            'ATR': {'timeperiod': 14}
        }
        print("✅ Technical indicators initialized")
        print("=== Initialization Complete ===\n")
    
    def fetch_data(self, symbol, interval='1d', period='6mo'):
        """Fetch historical price data"""
        print(f"\n=== Fetching Data for {symbol} ===")
        print(f"Timeframe: {interval}, Period: {period}")
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            print(f"✅ Data fetched successfully: {len(df)} periods")
            return df
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            return None
    
    def add_technical_indicators(self, df):
        """Add technical indicators to the dataframe"""
        try:
            # Create a copy of the dataframe
            df = df.copy()
            
            # Fill NaN values in price data first
            df['Close'] = df['Close'].ffill()
            df['High'] = df['High'].fillna(df['Close'])
            df['Low'] = df['Low'].fillna(df['Close'])
            df['Open'] = df['Open'].fillna(df['Close'])
            df['Volume'] = df['Volume'].fillna(0)
            
            print("Initial columns:", df.columns.tolist())
            
            # Add RSI
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(close=df['Close'], window=self.indicators['RSI']['timeperiod'])
            df['RSI'] = rsi.rsi()
            print("After RSI:", df.columns.tolist())
            
            # Add MACD
            from ta.trend import MACD
            macd = MACD(close=df['Close'],
                       window_slow=self.indicators['MACD']['slowperiod'],
                       window_fast=self.indicators['MACD']['fastperiod'],
                       window_sign=self.indicators['MACD']['signalperiod'])
            df['MACD_12_26_9'] = macd.macd()
            df['MACDs_12_26_9'] = macd.macd_signal()
            df['MACDh_12_26_9'] = macd.macd_diff()
            print("After MACD:", df.columns.tolist())
            
            # Add Bollinger Bands
            from ta.volatility import BollingerBands
            bb = BollingerBands(close=df['Close'],
                               window=self.indicators['BB']['timeperiod'],
                               window_dev=self.indicators['BB']['nbdevup'])
            df['BBU_20_2.0'] = bb.bollinger_hband()
            df['BBM_20_2.0'] = bb.bollinger_mavg()
            df['BBL_20_2.0'] = bb.bollinger_lband()
            print("After BB:", df.columns.tolist())
            
            # Add ATR
            from ta.volatility import AverageTrueRange
            atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'],
                                  window=self.indicators['ATR']['timeperiod'])
            df['ATR'] = atr.average_true_range()
            print("After ATR:", df.columns.tolist())
            
            # Calculate Returns and Volatility
            df['Returns'] = df['Close'].pct_change()
            df['Volatility'] = df['Returns'].rolling(5).std()
            
            # Fill any remaining NaN values
            df = df.ffill().bfill()
            
            print("Final columns:", df.columns.tolist())
            return df
        except Exception as e:
            print(f"Error adding indicators: {str(e)}")
            print("DataFrame head:", df.head())
            print("DataFrame info:", df.info())
            return df
    
    def detect_patterns(self, df, lookback=30):
        """Detect patterns in the price action using DeepSeek AI"""
        print("\n=== Starting Pattern Detection ===")
        try:
            recent_data = df.tail(lookback).copy()
            print(f"Analyzing last {lookback} periods")
            
            print("\n1. Getting Pattern Analysis...")
            pattern_analysis = self._get_pattern_analysis(recent_data)
            
            print("\n2. Getting Market Regime Analysis...")
            regime_analysis = self._get_market_regime(recent_data)
            
            print("\n3. Getting Price Prediction...")
            price_prediction = self._get_price_prediction(recent_data)
            
            print("\n4. Getting Support/Resistance Levels...")
            support_resistance = self._get_support_resistance(recent_data)
            
            print("\nPreparing response...")
            # Initialize default values for each analysis type
            default_pattern = json.dumps({
                "patterns": [],
                "quality_score": "N/A",
                "completion": "N/A"
            })
            
            default_regime = json.dumps({
                "regime": "Unknown",
                "confidence": "N/A",
                "characteristics": []
            })
            
            default_prediction = json.dumps({
                "price_target": "N/A",
                "confidence": "N/A",
                "key_factors": [],
                "risk_factors": []
            })
            
            default_sr = json.dumps({
                "support_levels": [],
                "resistance_levels": []
            })
            
            combined_analysis = {
                'patterns': pattern_analysis if pattern_analysis else default_pattern,
                'market_regime': regime_analysis if regime_analysis else default_regime,
                'price_prediction': price_prediction if price_prediction else default_prediction,
                'support_resistance': support_resistance if support_resistance else default_sr,
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ Analysis complete")
            return combined_analysis
            
        except Exception as e:
            print(f"❌ Error in pattern detection: {str(e)}")
            return {
                'patterns': json.dumps({"error": str(e), "patterns": [], "quality_score": "N/A", "completion": "N/A"}),
                'market_regime': json.dumps({"error": str(e), "regime": "Unknown", "confidence": "N/A", "characteristics": []}),
                'price_prediction': json.dumps({"error": str(e), "price_target": "N/A", "confidence": "N/A", "key_factors": [], "risk_factors": []}),
                'support_resistance': json.dumps({"error": str(e), "support_levels": [], "resistance_levels": []}),
                'timestamp': datetime.now().isoformat()
            }

    def _get_pattern_analysis(self, df):
        """Get AI-powered pattern analysis"""
        print("Making API call for pattern analysis...")
        
        # Format the price data as a simple string to avoid formatting issues
        price_data = df[['Open', 'High', 'Low', 'Close']].tail()
        price_str = "\n".join([f"Date {idx}: O:{row['Open']:.2f} H:{row['High']:.2f} L:{row['Low']:.2f} C:{row['Close']:.2f}" 
                             for idx, row in price_data.iterrows()])
        
        prompt = f"""Analyze the following price action and technical indicators to identify chart patterns:

Price Action (last 5 periods):
{price_str}

Technical Indicators:
RSI: {df['RSI'].iloc[-1]:.2f}
MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
BB Upper: {df['BBU_20_2.0'].iloc[-1]:.2f}
BB Lower: {df['BBL_20_2.0'].iloc[-1]:.2f}

Identify chart patterns and provide analysis. Return the response in this exact JSON format:
{{
    "patterns": ["pattern1", "pattern2"],
    "quality_score": 8,
    "completion": 85,
    "reliability": "high",
    "price_targets": [45000, 48000],
    "key_levels": [42000, 44000]
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:nitro",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                try:
                    # Validate JSON response
                    json_content = json.loads(content)
                    print("✅ Pattern analysis received and validated")
                    print(f"Received patterns: {json_content.get('patterns', [])}")
                    return content
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response from API: {e}")
                    return json.dumps({
                        "patterns": [],
                        "quality_score": "N/A",
                        "completion": "N/A",
                        "reliability": "N/A",
                        "price_targets": [],
                        "key_levels": []
                    })
            else:
                print(f"❌ API request failed: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Error in pattern analysis: {str(e)}")
            return None

    def _get_market_regime(self, df):
        """Detect current market regime using AI"""
        print("Making API call for market regime analysis...")
        
        # Format price and volume trends as simple strings
        price_trend = df['Close'].pct_change().tail()
        volume_trend = df['Volume'].pct_change().tail()
        
        price_trend_str = "\n".join([f"Day {i+1}: {val:.2%}" for i, val in enumerate(price_trend)])
        volume_trend_str = "\n".join([f"Day {i+1}: {val:.2%}" for i, val in enumerate(volume_trend)])
        
        prompt = f"""Analyze the following market data to determine the current market regime:

Volatility: {df['Volatility'].iloc[-1]:.4f}
ATR: {df['ATR'].iloc[-1]:.4f}

Price Trend (last 5 days):
{price_trend_str}

Volume Trend (last 5 days):
{volume_trend_str}

Return the response in this exact JSON format:
{{
    "regime": "Trending Up",
    "confidence": 85,
    "characteristics": [
        "Strong upward momentum",
        "Increasing volume",
        "Low volatility"
    ]
}}"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:nitro",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                try:
                    json_content = json.loads(content)
                    print("✅ Market regime analysis received and validated")
                    print(f"Detected regime: {json_content.get('regime', 'Unknown')} with {json_content.get('confidence', 'N/A')}% confidence")
                    return content
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response from API: {e}")
                    return json.dumps({
                        "regime": "Unknown",
                        "confidence": "N/A",
                        "characteristics": []
                    })
            else:
                print(f"❌ API request failed: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Error in market regime analysis: {str(e)}")
            return None

    def _get_price_prediction(self, df):
        """Get AI-powered price predictions"""
        print("Making API call for price prediction...")
        
        # Calculate BB position safely
        try:
            bb_position = ((df['Close'].iloc[-1] - df['BBL_20_2.0'].iloc[-1]) / 
                         (df['BBU_20_2.0'].iloc[-1] - df['BBL_20_2.0'].iloc[-1]))
        except:
            bb_position = 0.5  # Default to middle if calculation fails
        
        prompt = f"""Based on the following technical data, predict likely price movement:

Current Price: {df['Close'].iloc[-1]:.2f}
RSI: {df['RSI'].iloc[-1]:.2f}
MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
BB Position: {bb_position:.2f}
Volatility: {df['Volatility'].iloc[-1]:.4f}

Return the response in this exact JSON format:
{{
    "price_target": {df['Close'].iloc[-1]:.2f},
    "confidence": 75,
    "key_factors": [
        "RSI showing oversold conditions",
        "MACD bullish crossover",
        "Price near lower Bollinger Band"
    ],
    "risk_factors": [
        "High market volatility",
        "Resistance at {df['Close'].iloc[-1] * 1.05:.2f}"
    ],
    "alternative_scenarios": [
        {{
            "scenario": "Bearish",
            "target": {df['Close'].iloc[-1] * 0.95:.2f},
            "probability": 30
        }}
    ]
}}"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:nitro",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                try:
                    json_content = json.loads(content)
                    print("✅ Price prediction received and validated")
                    print(f"Price target: {json_content.get('price_target', 'N/A')} with {json_content.get('confidence', 'N/A')}% confidence")
                    return content
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response from API: {e}")
                    return json.dumps({
                        "price_target": str(df['Close'].iloc[-1]),
                        "confidence": "N/A",
                        "key_factors": [],
                        "risk_factors": [],
                        "alternative_scenarios": []
                    })
            else:
                print(f"❌ API request failed: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Error in price prediction: {str(e)}")
            return None

    def _get_support_resistance(self, df):
        """Identify support and resistance levels using AI"""
        print("Making API call for support/resistance analysis...")
        
        # Format price data as simple string
        price_stats = {
            'High': df['High'].max(),
            'Low': df['Low'].min(),
            'Current': df['Close'].iloc[-1],
            'Avg Volume': df['Volume'].mean()
        }
        
        prompt = f"""Analyze the following price data to identify key support and resistance levels:

Price Range:
High: {price_stats['High']:.2f}
Low: {price_stats['Low']:.2f}
Current: {price_stats['Current']:.2f}
Average Volume: {price_stats['Avg Volume']:.2f}

Return the response in this exact JSON format:
{{
    "support_levels": [
        {{"price": 40000, "strength": 8, "volume_confirmation": "high"}},
        {{"price": 38000, "strength": 6, "volume_confirmation": "medium"}}
    ],
    "resistance_levels": [
        {{"price": 44000, "strength": 7, "volume_confirmation": "high"}},
        {{"price": 46000, "strength": 5, "volume_confirmation": "low"}}
    ]
}}"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:nitro",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                try:
                    # Validate JSON response
                    json_content = json.loads(content)
                    print("✅ Support/Resistance analysis received and validated")
                    print(f"Found {len(json_content.get('support_levels', []))} support and {len(json_content.get('resistance_levels', []))} resistance levels")
                    return content
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response from API: {e}")
                    return json.dumps({
                        "support_levels": [],
                        "resistance_levels": []
                    })
            else:
                print(f"❌ API request failed: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Error in support/resistance analysis: {str(e)}")
            return None
    
    def plot_pattern(self, df, pattern_info):
        """Create an interactive plot with pattern annotations"""
        print("\n=== Generating Plot ===")
        try:
            fig = go.Figure()
            
            print("Adding candlestick chart...")
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ))
            
            print("Adding Bollinger Bands...")
            # Add upper band
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BBU_20_2.0'],
                name='BB Upper',
                line=dict(color='rgba(250, 250, 250, 0.3)', dash='dash')
            ))
            
            # Add middle band
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BBM_20_2.0'],
                name='BB Middle',
                line=dict(color='rgba(250, 250, 250, 0.2)')
            ))
            
            # Add lower band
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BBL_20_2.0'],
                name='BB Lower',
                line=dict(color='rgba(250, 250, 250, 0.3)', dash='dash'),
                fill='tonexty'
            ))
            
            print("Adding support and resistance levels...")
            if pattern_info and 'support_resistance' in pattern_info:
                try:
                    sr_data = json.loads(pattern_info['support_resistance'])
                    print("Support/Resistance data:", sr_data)
                    
                    # Add support levels
                    support_levels = sr_data.get('support_levels', [])
                    if isinstance(support_levels, list):
                        for level in support_levels:
                            if isinstance(level, dict) and 'price' in level:
                                try:
                                    price = float(level['price'])
                                    strength = level.get('strength', 'N/A')
                                    fig.add_hline(
                                        y=price,
                                        line=dict(color='rgba(0, 255, 0, 0.3)', dash='dash'),
                                        annotation_text=f"Support {price:.2f} (Strength: {strength})"
                                    )
                                except (ValueError, TypeError) as e:
                                    print(f"Error adding support level: {e}")
                    
                    # Add resistance levels
                    resistance_levels = sr_data.get('resistance_levels', [])
                    if isinstance(resistance_levels, list):
                        for level in resistance_levels:
                            if isinstance(level, dict) and 'price' in level:
                                try:
                                    price = float(level['price'])
                                    strength = level.get('strength', 'N/A')
                                    fig.add_hline(
                                        y=price,
                                        line=dict(color='rgba(255, 0, 0, 0.3)', dash='dash'),
                                        annotation_text=f"Resistance {price:.2f} (Strength: {strength})"
                                    )
                                except (ValueError, TypeError) as e:
                                    print(f"Error adding resistance level: {e}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing support/resistance data: {e}")
            
            print("Updating layout...")
            fig.update_layout(
                title='Price Action with Technical Patterns',
                yaxis_title='Price',
                xaxis_title='Date',
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.1)',
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.1)',
                ),
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            print("✅ Plot generated successfully")
            return fig
        except Exception as e:
            print(f"❌ Error generating plot: {str(e)}")
            print(f"Pattern info type: {type(pattern_info)}")
            if pattern_info:
                print(f"Pattern info content: {pattern_info}")
            return None 