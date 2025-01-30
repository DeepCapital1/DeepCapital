import streamlit as st
import pandas as pd
from pattern_detector import PatternDetector
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(
    page_title="Technical Analysis with DeepSeek AI",
    page_icon="📈",
    layout="wide"
)

# Initialize the pattern detector
@st.cache_resource
def get_detector():
    return PatternDetector()

detector = get_detector()

# App title and description
st.title("📊 Technical Analysis with DeepSeek AI")
st.markdown("""
This tool uses DeepSeek AI to identify complex chart patterns and provide detailed technical analysis.
It combines traditional technical indicators with AI-powered pattern recognition.
""")

# Sidebar controls
st.sidebar.header("Settings")

# Symbol input
symbol = st.sidebar.text_input(
    "Enter Symbol (e.g., BTC-USD)",
    value="BTC-USD",
    help="Enter a valid trading symbol (e.g., BTC-USD, ETH-USD, AAPL)"
)

# Timeframe selection
interval = st.sidebar.selectbox(
    "Select Timeframe",
    options=['1d', '1h', '15m', '5m'],
    index=0,
    help="Select the timeframe for analysis"
)

# Period selection
period = st.sidebar.selectbox(
    "Select Period",
    options=['1mo', '3mo', '6mo', '1y'],
    index=1,
    help="Select the historical data period"
)

# Analysis button
if st.sidebar.button("Analyze"):
    with st.spinner("Fetching and analyzing data..."):
        try:
            # Fetch data
            df = detector.fetch_data(symbol, interval, period)
            
            if df is not None:
                # Add technical indicators
                df = detector.add_technical_indicators(df)
                
                # Get AI analysis
                analysis = detector.detect_patterns(df)
                
                # Create two columns
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Price Chart with Technical Indicators")
                    fig = detector.plot_pattern(df, analysis)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("DeepSeek AI Analysis")
                    
                    # Pattern Analysis
                    with st.expander("🎯 Pattern Analysis", expanded=True):
                        if analysis['patterns']:
                            pattern_data = json.loads(analysis['patterns'])
                            st.write("**Detected Patterns:**")
                            for pattern in pattern_data.get('patterns', []):
                                st.write(f"- {pattern}")
                            st.write(f"**Quality Score:** {pattern_data.get('quality_score', 'N/A')}/10")
                            st.write(f"**Completion:** {pattern_data.get('completion', 'N/A')}%")
                    
                    # Market Regime
                    with st.expander("🌊 Market Regime", expanded=True):
                        if analysis['market_regime']:
                            regime_data = json.loads(analysis['market_regime'])
                            st.write(f"**Current Regime:** {regime_data.get('regime', 'Unknown')}")
                            st.write(f"**Confidence:** {regime_data.get('confidence', 'N/A')}%")
                            st.write("**Characteristics:**")
                            for char in regime_data.get('characteristics', []):
                                st.write(f"- {char}")
                    
                    # Price Prediction
                    with st.expander("🎯 Price Prediction", expanded=True):
                        if analysis['price_prediction']:
                            pred_data = json.loads(analysis['price_prediction'])
                            st.write(f"**Target (24h):** {pred_data.get('price_target', 'N/A')}")
                            st.write(f"**Confidence:** {pred_data.get('confidence', 'N/A')}%")
                            st.write("**Key Factors:**")
                            for factor in pred_data.get('key_factors', []):
                                st.write(f"- {factor}")
                            st.write("**Risk Factors:**")
                            for risk in pred_data.get('risk_factors', []):
                                st.write(f"- {risk}")
                    
                    # Support/Resistance
                    with st.expander("📊 Support & Resistance", expanded=True):
                        if analysis['support_resistance']:
                            sr_data = json.loads(analysis['support_resistance'])
                            st.write("**Support Levels:**")
                            for level in sr_data.get('support_levels', []):
                                st.write(f"- Price: {level['price']}, Strength: {level['strength']}/10")
                            st.write("**Resistance Levels:**")
                            for level in sr_data.get('resistance_levels', []):
                                st.write(f"- Price: {level['price']}, Strength: {level['strength']}/10")
                    
                    # Timestamp
                    st.caption(f"Last updated: {datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.error("Error fetching data. Please check the symbol and try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add documentation
with st.sidebar.expander("ℹ️ About"):
    st.write("""
    This app combines traditional technical analysis with DeepSeek AI to provide comprehensive market insights:
    
    - **Pattern Analysis**: Identifies chart patterns and their reliability
    - **Market Regime**: Determines the current market state
    - **Price Prediction**: AI-powered price targets and scenarios
    - **Support/Resistance**: Dynamic level detection with strength scoring
    
    All analysis is powered by DeepSeek's advanced AI models.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Powered by DeepSeek AI") 