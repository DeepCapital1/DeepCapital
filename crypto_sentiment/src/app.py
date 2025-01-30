import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sentiment_analyzer import SentimentAnalyzer
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import requests
import os
from dotenv import load_dotenv

def async_to_sync(f):
    """Convert async function to sync function"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

def test_openrouter():
    """Test if OpenRouter API is working with deepseek-r1-distill-llama-70b"""
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    st.write("Testing OpenRouter API...")
    st.write("API Key:", api_key[:10] + "..." if api_key else "Not found")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:8501',
        'X-Title': 'Crypto Sentiment Analyzer'
    }
    
    try:
        # Test with deepseek-r1:nitro model
        test_prompt = "What is 2+2? Explain your reasoning step by step."
        st.write("\nTesting API call with deepseek-r1:nitro...")
        
        request_body = {
            "model": "deepseek/deepseek-r1:nitro",
            "messages": [{"role": "user", "content": test_prompt}]
        }
        
        st.write("Request body:", request_body)
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=request_body
        )
        
        st.write("Response status code:", response.status_code)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']
            st.success("OpenRouter API is working!")
            st.write("Model Response:", result.get('content', 'No content'))
            
            # Check if the response includes reasoning
            if 'reasoning_content' in result:
                st.success("✨ Model supports Chain of Thought reasoning!")
                st.write("Reasoning Process:", result['reasoning_content'])
            else:
                st.info("Using deepseek-r1:nitro for enhanced reasoning capabilities.")
                
                # Show the model's response to see if it includes step-by-step reasoning in the content
                response_content = result.get('content', '')
                if 'step' in response_content.lower():
                    st.success("But the model did provide step-by-step reasoning in its response!")
                    st.write("Steps found in response:", response_content)
        else:
            st.error(f"OpenRouter API error: {response.status_code}")
            st.write("Error details:", response.text)
            
    except Exception as e:
        st.error(f"Failed to connect to OpenRouter API: {str(e)}")
        import traceback
        st.write("Full error:", traceback.format_exc())

st.set_page_config(
    page_title="Crypto Sentiment Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialize the sentiment analyzer
@st.cache_resource
def get_analyzer():
    try:
        analyzer = SentimentAnalyzer()
        return analyzer
    except Exception as e:
        st.error(f"Failed to initialize the analyzer: {str(e)}")
        return None

analyzer = get_analyzer()

if analyzer is None:
    st.error("Could not initialize the sentiment analyzer. Please check your API credentials in the .env file.")
    st.stop()

# App title and description
st.title("🚀 Crypto Sentiment Analyzer")
st.markdown("""
This tool analyzes cryptocurrency-related text using DeepSeek's chain-of-thought reasoning
to provide detailed sentiment analysis and market insights.
""")

# Sidebar for input options
st.sidebar.header("Analysis Options")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis Type",
    ["Crypto Ticker Analysis", "Single Text Analysis", "Multiple Sources Analysis"]
)

# Add test button in sidebar
st.sidebar.header("Debug Options")
if st.sidebar.button("Test OpenRouter API"):
    test_openrouter()

if analysis_type == "Crypto Ticker Analysis":
    st.subheader("Crypto Ticker Analysis")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Crypto Ticker (e.g., $BTC, $ETH, $PNUT)",
            placeholder="$BTC"
        )
    
    with col2:
        hours = st.number_input(
            "Hours of Historical Data",
            min_value=1,
            max_value=72,
            value=24
        )
    
    with col3:
        max_tweets = st.number_input(
            "Maximum Tweets",
            min_value=10,
            max_value=100,
            value=50,
            help="Maximum number of tweets to analyze (10-100)"
        )
    
    if st.button("Analyze Ticker"):
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        
        with st.spinner(""):
            try:
                # Show initial status
                status_placeholder.info("🔄 Starting analysis for " + ticker)
                
                # Initialize Twitter functionality only when needed
                try:
                    status_placeholder.info("🔄 Initializing Twitter connection...")
                    asyncio.run(analyzer.init())
                except Exception as e:
                    status_placeholder.error("❌ Failed to connect to Twitter. Please check your credentials.")
                    st.error(f"Technical details: {str(e)}")
                    st.stop()
                
                # Create a progress message function
                def update_progress(message):
                    status_placeholder.info(f"🔄 {message}")
                
                # Get the analysis result with progress updates
                result = asyncio.run(analyzer.analyze_crypto_ticker(ticker, hours, max_tweets, update_progress))
                
                if 'error' in result:
                    status_placeholder.error(f"""
                    ❌ {result['error']}
                    
                    This might be a temporary issue as we're still in development.
                    Please try clicking 'Analyze Ticker' again in a few seconds.
                    """)
                else:
                    # Show success and results
                    status_placeholder.success("✅ Analysis complete!")
                    
                    with result_placeholder.container():
                        # Display overall sentiment and stats
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Weighted Sentiment", f"{result['weighted_sentiment']:.2f}")
                            st.metric("Tweet Count", result['stats']['tweet_count'])
                        with col2:
                            st.metric("Average Engagement", f"{result['stats']['avg_engagement']:.1f}")
                            sentiment_range = result['stats']['sentiment_range']
                            st.metric("Sentiment Range", f"{sentiment_range['min']:.2f} to {sentiment_range['max']:.2f}")
                        
                        # Display the analysis
                        st.header("Analysis Summary")
                        
                        # Format and display the analysis content
                        analysis_text = result['analysis_content']
                        
                        # Split into sections
                        sections = analysis_text.split('\n\n')
                        
                        for section in sections:
                            if section.strip():
                                # Check if it's a header
                                if section.startswith(('Analysis Summary', 'Comprehensive Analysis')):
                                    st.subheader(section.strip())
                                # Check if it's a numbered section
                                elif any(section.startswith(str(i) + '.') for i in range(1, 6)):
                                    st.subheader(section.split('\n')[0].strip())
                                    # Display the content after the header
                                    content = '\n'.join(section.split('\n')[1:])
                                    st.write(content.strip())
                                # Check if it's the conclusion
                                elif section.lower().startswith('conclusion'):
                                    st.subheader("Conclusion")
                                    st.write(section[len('Conclusion:'):].strip())
                                else:
                                    st.write(section.strip())
                        
                        # Show detailed tweet analysis in an expander
                        with st.expander("🔍 View Individual Tweet Analysis"):
                            st.write("Here are the individual tweets I analyzed:")
                            for idx, analysis in enumerate(result['individual_analyses'], 1):
                                st.markdown(f"**Tweet {idx}**")
                                st.markdown(f"*Sentiment: {analysis['sentiment_score']:.2f} | "
                                          f"Engagement: {analysis['engagement']}*")
                                st.text(analysis['text'][:200] + "..." if len(analysis['text']) > 200 else analysis['text'])
                                st.markdown("---")
                    
            except Exception as e:
                status_placeholder.error("""
                🔄 Oops! Something went wrong. We're still in development, so this might happen occasionally.
                
                Please try:
                1. Waiting a few seconds
                2. Clicking 'Analyze Ticker' again
                3. Making sure your ticker symbol is correct (e.g., $BTC, $ETH)
                
                If the problem persists, it might be due to:
                - Twitter API limitations
                - Network connectivity issues
                - Service maintenance
                """)
                st.error(f"Technical details: {str(e)}")

elif analysis_type == "Single Text Analysis":
    # Single text analysis
    text_input = st.text_area(
        "Enter text to analyze",
        height=150,
        placeholder="Enter cryptocurrency-related text here..."
    )
    
    if st.button("Analyze Sentiment"):
        if text_input:
            with st.spinner("Analyzing sentiment..."):
                try:
                    result = analyzer.analyze_text(text_input)
                    
                    # Display results in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Sentiment Score")
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=result['sentiment_score'],
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [-1, 1]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [-1, -0.3], 'color': "red"},
                                    {'range': [-0.3, 0.3], 'color': "gray"},
                                    {'range': [0.3, 1], 'color': "green"}
                                ]
                            }
                        ))
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.subheader("Detailed Analysis")
                        st.write(result['analysis'])
                    
                    st.subheader("Chain of Thought Breakdown")
                    steps = result['analysis'].split('\n')
                    for i, step in enumerate(steps, 1):
                        if step.strip():
                            st.markdown(f"**Step {i}:** {step}")
                except Exception as e:
                    st.error(f"Error analyzing text: {str(e)}")

else:
    # Multiple sources analysis
    num_sources = st.sidebar.number_input("Number of sources", min_value=2, max_value=10, value=3)
    
    texts = []
    for i in range(num_sources):
        text = st.text_area(f"Source {i+1}", height=100, key=f"source_{i}")
        texts.append(text)
    
    if st.button("Analyze Multiple Sources"):
        if all(texts):
            with st.spinner("Analyzing multiple sources..."):
                try:
                    result = analyzer.analyze_multiple_sources(texts)
                    
                    if result:
                        # Display aggregate results
                        st.subheader("Aggregate Sentiment Analysis")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=result['average_sentiment'],
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [-1, 1]},
                                    'bar': {'color': "darkblue"},
                                    'steps': [
                                        {'range': [-1, -0.3], 'color': "red"},
                                        {'range': [-0.3, 0.3], 'color': "gray"},
                                        {'range': [0.3, 1], 'color': "green"}
                                    ]
                                }
                            ))
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.metric("Standard Deviation", f"{result['sentiment_std']:.3f}")
                            
                        # Display individual results
                        st.subheader("Individual Source Analysis")
                        for i, analysis in enumerate(result['individual_results'], 1):
                            with st.expander(f"Source {i} Analysis"):
                                st.write(f"**Sentiment Score:** {analysis['sentiment_score']:.3f}")
                                st.write("**Analysis:**")
                                st.write(analysis['analysis'])
                except Exception as e:
                    st.error(f"Error analyzing sources: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using DeepSeek's Chain-of-Thought Reasoning</p>
</div>
""", unsafe_allow_html=True) 