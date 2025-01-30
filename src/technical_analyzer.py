import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import json
import requests
from pattern_detector import PatternDetector

class TechnicalAnalyzer:
    def __init__(self):
        self.supported_indicators = {
            'RSI': self._calculate_rsi,
            'MACD': self._calculate_macd,
            'Bollinger Bands': self._calculate_bollinger_bands,
            'Moving Averages': self._calculate_moving_averages
        }
        try:
            # Initialize pattern detector
            self.pattern_detector = PatternDetector()
        except Exception as e:
            print(f"Warning: Pattern detector initialization failed: {str(e)}")
            self.pattern_detector = None

    def get_crypto_data(self, symbol, period='1y', interval='1d'):
        """
        Fetch cryptocurrency data from Yahoo Finance
        """
        try:
            # Add -USD suffix if not present
            if not symbol.endswith('-USD'):
                symbol = f"{symbol}-USD"
            
            data = yf.download(symbol, period=period, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Add technical indicators used by pattern detector
            if self.pattern_detector:
                data = self.pattern_detector.add_technical_indicators(data)
            return data
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    def analyze_crypto(self, symbol, indicators, period='1y', interval='1d'):
        """
        Perform technical analysis on a cryptocurrency
        """
        try:
            data = self.get_crypto_data(symbol, period, interval)
            results = {'data': data, 'indicators': {}}
            
            # Add basic technical indicators
            for indicator in indicators:
                if indicator in self.supported_indicators:
                    results['indicators'][indicator] = self.supported_indicators[indicator](data)
            
            # Add pattern detection results if available
            if self.pattern_detector:
                try:
                    # Get comprehensive analysis from pattern detector
                    pattern_analysis, _ = self.pattern_detector.analyze(symbol, interval, period)
                    if pattern_analysis:
                        results['patterns'] = pattern_analysis
                except Exception as e:
                    print(f"Warning: Pattern analysis failed: {str(e)}")
                    results['patterns'] = {
                        'technical_patterns': {
                            'detected_patterns': [],
                            'quality_score': 0,
                            'reliability': 'unknown'
                        },
                        'market_regime': {
                            'regime': 'Unknown',
                            'confidence': 0,
                            'trend_strength': 0,
                            'volatility_regime': 'Unknown'
                        }
                    }
            
            return results
        except Exception as e:
            raise Exception(f"Error in technical analysis: {str(e)}")

    def _calculate_rsi(self, data, period=14):
        """Calculate RSI indicator"""
        try:
            rsi = ta.momentum.RSIIndicator(data['Close'], window=period)
            return {
                'values': rsi.rsi(),
                'period': period
            }
        except Exception as e:
            raise Exception(f"Error calculating RSI: {str(e)}")

    def _calculate_macd(self, data):
        """Calculate MACD indicator"""
        try:
            macd = ta.trend.MACD(data['Close'])
            return {
                'macd': macd.macd(),
                'signal': macd.macd_signal(),
                'histogram': macd.macd_diff()
            }
        except Exception as e:
            raise Exception(f"Error calculating MACD: {str(e)}")

    def _calculate_bollinger_bands(self, data, window=20, window_dev=2):
        """Calculate Bollinger Bands"""
        try:
            bollinger = ta.volatility.BollingerBands(data['Close'], window=window, window_dev=window_dev)
            return {
                'high_band': bollinger.bollinger_hband(),
                'mid_band': bollinger.bollinger_mavg(),
                'low_band': bollinger.bollinger_lband()
            }
        except Exception as e:
            raise Exception(f"Error calculating Bollinger Bands: {str(e)}")

    def _calculate_moving_averages(self, data):
        """Calculate various moving averages"""
        try:
            return {
                'SMA_20': ta.trend.sma_indicator(data['Close'], window=20),
                'SMA_50': ta.trend.sma_indicator(data['Close'], window=50),
                'SMA_200': ta.trend.sma_indicator(data['Close'], window=200),
                'EMA_20': ta.trend.ema_indicator(data['Close'], window=20)
            }
        except Exception as e:
            raise Exception(f"Error calculating Moving Averages: {str(e)}")

    def create_technical_analysis_plot(self, results, selected_indicators):
        """Create a comprehensive technical analysis plot"""
        try:
            data = results['data']
            rows = len(selected_indicators) + 1  # +1 for price chart
            
            # Create figure with secondary y-axis for volume
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                              vertical_spacing=0.05,
                              row_heights=[0.5] + [0.5/(rows-1)]*(rows-1))

            # Add price candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Price'
                ),
                row=1, col=1
            )

            # Add volume bars
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color='rgba(0,0,0,0.2)'
                ),
                row=1, col=1
            )

            # Add patterns if available
            if 'patterns' in results:
                patterns = results['patterns']
                if 'market_regime' in patterns:
                    regime = patterns['market_regime']
                    fig.add_annotation(
                        text=f"Market Regime: {regime['regime']} ({regime['confidence']}% confidence)",
                        xref="paper", yref="paper",
                        x=0, y=1.1,
                        showarrow=False,
                        font=dict(size=12)
                    )

                if 'price_prediction' in patterns:
                    pred = patterns['price_prediction']
                    if pred.get('support_level'):
                        fig.add_hline(
                            y=pred['support_level'],
                            line_dash="dot",
                            line_color="green",
                            annotation_text="Support",
                            row=1, col=1
                        )
                    if pred.get('resistance_level'):
                        fig.add_hline(
                            y=pred['resistance_level'],
                            line_dash="dot",
                            line_color="red",
                            annotation_text="Resistance",
                            row=1, col=1
                        )

            current_row = 2
            for indicator in selected_indicators:
                if indicator == 'RSI':
                    rsi_values = results['indicators']['RSI']['values']
                    fig.add_trace(
                        go.Scatter(x=data.index, y=rsi_values, name='RSI'),
                        row=current_row, col=1
                    )
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)

                elif indicator == 'MACD':
                    macd_data = results['indicators']['MACD']
                    fig.add_trace(
                        go.Scatter(x=data.index, y=macd_data['macd'], name='MACD'),
                        row=current_row, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=data.index, y=macd_data['signal'], name='Signal'),
                        row=current_row, col=1
                    )

                elif indicator == 'Bollinger Bands':
                    bb_data = results['indicators']['Bollinger Bands']
                    fig.add_trace(
                        go.Scatter(x=data.index, y=bb_data['high_band'], name='Upper BB', line=dict(dash='dash')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=data.index, y=bb_data['mid_band'], name='Middle BB', line=dict(dash='dash')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=data.index, y=bb_data['low_band'], name='Lower BB', line=dict(dash='dash')),
                        row=1, col=1
                    )
                    continue  # Don't increment row as BB is on price chart

                elif indicator == 'Moving Averages':
                    ma_data = results['indicators']['Moving Averages']
                    for ma_name, ma_values in ma_data.items():
                        fig.add_trace(
                            go.Scatter(x=data.index, y=ma_values, name=ma_name),
                            row=1, col=1
                        )
                    continue  # Don't increment row as MAs are on price chart

                current_row += 1

            # Update layout
            fig.update_layout(
                height=200 * rows,
                title_text="Technical Analysis Chart",
                xaxis_rangeslider_visible=False,
                showlegend=True
            )

            return fig
        except Exception as e:
            raise Exception(f"Error creating technical analysis plot: {str(e)}") 