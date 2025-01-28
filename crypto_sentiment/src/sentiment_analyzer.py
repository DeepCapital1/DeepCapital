import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from data_collector import DataCollector
import asyncio
import streamlit as st

class SentimentAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenRouter API credentials not configured")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8501',
            'X-Title': 'Crypto Sentiment Analyzer'
        }
        
        # Initialize data collector
        self.data_collector = DataCollector()
        
    async def init(self):
        """Initialize the data collector"""
        await self.data_collector.init()

    def analyze_text(self, text):
        """
        Analyze the sentiment of a given text using DeepSeek's step-by-step reasoning.
        Returns a detailed sentiment analysis with explanation.
        """
        prompt = f"""Analyze the sentiment of this crypto-related text. Follow these steps:
        1. Identify key sentiment indicators
        2. Consider market impact and technical factors
        3. Evaluate overall sentiment
        4. Provide a sentiment score from -1 (very negative) to 1 (very positive)
        
        Text: {text}
        
        Provide your analysis in clear steps and end with a numerical score."""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:nitro",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']
                analysis = result['content']
                
                # Extract sentiment score using simple heuristics
                try:
                    # Look for numerical score in the response
                    score = float([line for line in analysis.split('\n') 
                                if any(x in line.lower() for x in ['score:', 'score is:', 'sentiment:', 'rating:'])][-1]
                                .split(':')[-1].strip().split()[0])
                except:
                    # Fallback to sentiment keywords
                    score = self._extract_sentiment_score(analysis)
                
                return {
                    'text': text,
                    'analysis': analysis,
                    'sentiment_score': score,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"API request failed with status code: {response.status_code}")
                print("Response text:", response.text)
                raise Exception(f"API request failed with status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error in analyze_text: {str(e)}")
            raise e

    def _extract_sentiment_score(self, analysis):
        """
        Extract sentiment score from analysis text using keyword matching.
        """
        positive_words = ['bullish', 'positive', 'optimistic', 'growth', 'gain']
        negative_words = ['bearish', 'negative', 'pessimistic', 'decline', 'loss']
        
        analysis_lower = analysis.lower()
        positive_count = sum(analysis_lower.count(word) for word in positive_words)
        negative_count = sum(analysis_lower.count(word) for word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0
        
        return (positive_count - negative_count) / total

    def analyze_multiple_sources(self, texts):
        """
        Analyze sentiment from multiple text sources and aggregate results.
        """
        results = []
        for text in texts:
            try:
                result = self.analyze_text(text)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing text: {str(e)}")
                continue
        
        if not results:
            return None
        
        df = pd.DataFrame(results)
        
        return {
            'individual_results': results,
            'average_sentiment': df['sentiment_score'].mean(),
            'sentiment_std': df['sentiment_score'].std(),
            'timestamp': datetime.now().isoformat()
        }

    def get_market_correlation(self, sentiment_scores, price_changes):
        """
        Calculate correlation between sentiment scores and price changes.
        """
        if len(sentiment_scores) != len(price_changes):
            raise ValueError("Length of sentiment scores and price changes must match")
        
        correlation = np.corrcoef(sentiment_scores, price_changes)[0, 1]
        return {
            'correlation': correlation,
            'interpretation': self._interpret_correlation(correlation),
            'timestamp': datetime.now().isoformat()
        }

    def _interpret_correlation(self, correlation):
        """
        Interpret the correlation coefficient with detailed explanation.
        """
        if correlation > 0.7:
            return "Strong positive correlation: Sentiment strongly predicts price movements"
        elif correlation > 0.3:
            return "Moderate positive correlation: Sentiment somewhat predicts price movements"
        elif correlation > -0.3:
            return "Weak correlation: Sentiment has limited predictive value"
        elif correlation > -0.7:
            return "Moderate negative correlation: Sentiment inversely predicts price movements"
        else:
            return "Strong negative correlation: Sentiment strongly inversely predicts price movements"

    async def analyze_crypto_ticker(self, ticker, hours_back=24):
        """
        Optimized analysis of a crypto ticker using Twitter data.
        """
        print(f"\n🔄 Starting analysis for {ticker}")
        
        # Collect data
        print("\n🔎 Searching for recent tweets...")
        data = await self.data_collector.aggregate_data(ticker, hours_back)
        if data.empty:
            print("❌ No tweets found")
            return {
                'error': f'No tweets found for {ticker} in the past {hours_back} hours. Please try again.',
                'timestamp': datetime.now().isoformat()
            }

        # Analyze each source
        total_tweets = len(data)
        print(f"\n📊 Found {total_tweets} tweets to analyze")
        analyses = []
        
        print("\n🧠 Starting sentiment analysis...")
        for idx, row in enumerate(data.iterrows(), 1):
            _, row = row
            try:
                print(f"\n📝 Analyzing tweet {idx}/{total_tweets}")
                
                analysis = self.analyze_text(row['text'])
                analysis['source'] = 'twitter'
                analysis['engagement'] = row.get('engagement', 0)
                
                print(f"Sentiment: {analysis['sentiment_score']:.2f}")
                if analysis['engagement']:
                    print(f"Engagement: {analysis['engagement']}")
                
                analyses.append(analysis)
            except Exception as e:
                print(f"⚠️ Error with tweet {idx}: {str(e)}")
                continue

        if not analyses:
            print("❌ Could not analyze any tweets")
            return {
                'error': 'Unable to analyze tweets. This might be temporary - please try again.',
                'timestamp': datetime.now().isoformat()
            }

        print(f"\n✅ Successfully analyzed {len(analyses)} tweets")

        # Calculate weighted sentiment score
        print("\n📊 Calculating overall sentiment...")
        df = pd.DataFrame(analyses)
        
        # Handle engagement weights
        if df['engagement'].sum() > 0:
            df['weight'] = df['engagement'] / df['engagement'].max()  # Normalize engagement scores
            print("Using engagement-weighted sentiment")
        else:
            # If no engagement, use equal weights
            df['weight'] = 1.0
            print("Using equally-weighted sentiment")
            
        weighted_sentiment = (df['sentiment_score'] * df['weight']).sum() / df['weight'].sum()
        print(f"📈 Overall sentiment score: {weighted_sentiment:.2f}")

        # Generate summary using DeepSeek
        print("\n🤖 Generating comprehensive analysis...")
        summary_prompt = f"""Generate a comprehensive market analysis for {ticker} with the following structure:

        Analysis Summary
        Comprehensive Analysis of {ticker}

        1. Overall Market Sentiment & Confidence Level
        - Analyze the weighted sentiment score of {weighted_sentiment:.2f}
        - Evaluate confidence based on sample size ({len(analyses)} sources)
        - Consider sentiment distribution and conviction level

        2. Key Factors Driving Sentiment
        - Analyze social media activity patterns and their implications
        - Evaluate the quality and impact of discussions
        - Identify any notable sentiment biases or trends

        3. Potential Price Impact Analysis
        - Assess short-term volatility expectations
        - Consider liquidity and market cap implications
        - Evaluate catalyst dependency and potential price movements

        4. Risk Factors to Consider
        - Identify social media sentiment risks
        - Evaluate market structure risks
        - Consider macro and token-specific risks

        5. Short-Term Outlook (24-48 Hours)
        - Provide baseline scenario expectations
        - Identify potential bearish and bullish triggers
        - Include specific recommendations for traders

        End with a clear conclusion summarizing the key points.
        Format the response with clear sections, bullet points, and specific details.
        Include quantitative metrics where relevant (e.g., percentage ranges for price movements).

        Context:
        - Weighted sentiment score: {weighted_sentiment:.2f}
        - Number of sources analyzed: {len(analyses)}
        - Sentiment range: {df['sentiment_score'].min():.2f} to {df['sentiment_score'].max():.2f}
        - Common themes: {', '.join(self._extract_common_themes(df['analysis'].tolist()))}"""

        print("Making final API request...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=self.headers,
            json={
                "model": "deepseek/deepseek-r1:nitro",
                "messages": [{"role": "user", "content": summary_prompt}]
            }
        )

        if response.status_code == 200:
            result = response.json()['choices'][0]['message']
            analysis_text = result['content']
            print("✅ Analysis complete!")
        else:
            print(f"⚠️ Error generating final analysis: {response.status_code}")
            analysis_text = "Failed to generate analysis"

        print("\n🎉 All done!")
        return {
            'ticker': ticker,
            'weighted_sentiment': weighted_sentiment,
            'individual_analyses': analyses,
            'analysis_content': analysis_text,
            'stats': {
                'tweet_count': len(analyses),
                'sentiment_mean': df['sentiment_score'].mean(),
                'sentiment_std': df['sentiment_score'].std(),
                'sentiment_range': {
                    'min': df['sentiment_score'].min(),
                    'max': df['sentiment_score'].max()
                },
                'avg_engagement': df['engagement'].mean()
            },
            'timestamp': datetime.now().isoformat()
        }

    def _extract_common_themes(self, analyses, min_occurrences=2):
        """Extract common themes from sentiment analyses"""
        # Common crypto sentiment-related keywords
        themes = {
            'bullish': ['bullish', 'uptrend', 'growth', 'rally', 'surge'],
            'bearish': ['bearish', 'downtrend', 'decline', 'dump', 'crash'],
            'momentum': ['momentum', 'volume', 'breakout', 'resistance', 'support'],
            'fundamental': ['adoption', 'development', 'partnership', 'news', 'update'],
            'risk': ['risk', 'volatile', 'uncertainty', 'caution', 'warning']
        }
        
        # Count occurrences of each theme
        theme_counts = {theme: 0 for theme in themes}
        
        for analysis in analyses:
            analysis_lower = analysis.lower()
            for theme, keywords in themes.items():
                if any(keyword in analysis_lower for keyword in keywords):
                    theme_counts[theme] += 1
        
        # Return themes that appear multiple times
        common_themes = [theme for theme, count in theme_counts.items() 
                        if count >= min_occurrences]
        
        return common_themes if common_themes else ['neutral'] 