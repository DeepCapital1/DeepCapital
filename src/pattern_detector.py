def _get_market_regime(self, df):
        """Detect current market regime using AI"""
        print("\nMaking API call for market regime analysis...")
        
        # Calculate additional technical indicators for context
        last_close = df['Close'].iloc[-1]
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        vol_change = df['Volume'].pct_change().tail(5).mean()
        price_change = df['Close'].pct_change().tail(5).mean()
        
        prompt = f"""Analyze the following market data and return a JSON response describing the market regime:

Technical Data:
- Current Price: {last_close:.2f}
- RSI: {df['RSI'].iloc[-1]:.2f}
- MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
- 20 SMA: {sma_20:.2f}
- 50 SMA: {sma_50:.2f}
- 5-day Volume Change: {vol_change:.2%}
- 5-day Price Change: {price_change:.2%}

Return ONLY a valid JSON object in this exact format:
{{
    "regime": "string",
    "confidence": number,
    "characteristics": ["string"],
    "trend_strength": number,
    "volatility_regime": "string"
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b",
                    "messages": [
                        {"role": "system", "content": "You are a market analysis AI. Respond only with valid JSON objects. For regime, use one of: ['Trending Up', 'Trending Down', 'Ranging', 'Accumulation', 'Distribution']. For volatility_regime use one of: ['Low', 'Moderate', 'High']."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 150
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Full API Response:", result)
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content'].strip()
                        print("Raw Content:", content)
                        
                        # Try to clean the content if it has markdown code blocks
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        json_content = json.loads(content)
                        required_fields = ['regime', 'confidence', 'characteristics', 'trend_strength', 'volatility_regime']
                        if all(field in json_content for field in required_fields):
                            print("✅ Market regime analysis received and validated")
                            print(f"Detected regime: {json_content['regime']} with {json_content['confidence']}% confidence")
                            return json.dumps(json_content)
                        else:
                            raise ValueError("Missing required fields in JSON response")
                    else:
                        raise ValueError("No choices in API response")
                except Exception as e:
                    print(f"❌ Error processing API response: {str(e)}")
                    print("Raw response content:", content if 'content' in locals() else "No content")
                    return json.dumps({
                        "regime": "Unknown",
                        "confidence": 0,
                        "characteristics": ["Analysis failed - invalid response format"],
                        "trend_strength": 0,
                        "volatility_regime": "Unknown"
                    })
            else:
                print(f"❌ API request failed: {response.text}")
                return json.dumps({
                    "regime": "Unknown",
                    "confidence": 0,
                    "characteristics": ["Analysis failed - API error"],
                    "trend_strength": 0,
                    "volatility_regime": "Unknown"
                })
        except Exception as e:
            print(f"❌ Error in market regime analysis: {str(e)}")
            return json.dumps({
                "regime": "Unknown",
                "confidence": 0,
                "characteristics": ["Analysis failed - system error"],
                "trend_strength": 0,
                "volatility_regime": "Unknown"
            })

def _get_price_prediction(self, df):
        """Get AI-powered price predictions"""
        print("\nMaking API call for price prediction...")
        
        current_price = df['Close'].iloc[-1]
        bb_width = (df['BBU_20_2.0'] - df['BBL_20_2.0']) / df['BBM_20_2.0']
        bb_position = (current_price - df['BBL_20_2.0']) / (df['BBU_20_2.0'] - df['BBL_20_2.0'])
        
        prompt = f"""Analyze the following market data and return a JSON response with price predictions:

Technical Data:
- Current Price: {current_price:.2f}
- RSI: {df['RSI'].iloc[-1]:.2f}
- MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
- MACD Signal: {df['MACDs_12_26_9'].iloc[-1]:.2f}
- BB Width: {bb_width.iloc[-1]:.4f}
- BB Position: {bb_position.iloc[-1]:.4f}
- ATR: {df['ATR'].iloc[-1]:.2f}
- Volatility: {df['Volatility'].iloc[-1]:.4f}

Return ONLY a valid JSON object in this exact format:
{{
    "price_target": number,
    "confidence": number,
    "timeframe": "string",
    "key_factors": ["string"],
    "risk_factors": ["string"],
    "support_level": number,
    "resistance_level": number
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b",
                    "messages": [
                        {"role": "system", "content": "You are a market analysis AI. Respond only with valid JSON objects. For timeframe use one of: ['Short-term (1-3 days)', 'Medium-term (1-2 weeks)', 'Long-term (1+ month)']. Price targets should be within ±15% of current price."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 250
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Full API Response:", result)
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content'].strip()
                        print("Raw Content:", content)
                        
                        # Try to clean the content if it has markdown code blocks
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        json_content = json.loads(content)
                        required_fields = ['price_target', 'confidence', 'timeframe', 'key_factors', 'risk_factors', 'support_level', 'resistance_level']
                        if all(field in json_content for field in required_fields):
                            print("✅ Price prediction received and validated")
                            print(f"Price target: {json_content['price_target']} ({json_content['timeframe']}) with {json_content['confidence']}% confidence")
                            return json.dumps(json_content)
                        else:
                            raise ValueError("Missing required fields in JSON response")
                    else:
                        raise ValueError("No choices in API response")
                except Exception as e:
                    print(f"❌ Error processing API response: {str(e)}")
                    print("Raw response content:", content if 'content' in locals() else "No content")
                    return json.dumps({
                        "price_target": current_price,
                        "confidence": 0,
                        "timeframe": "Unknown",
                        "key_factors": ["Analysis failed - invalid response format"],
                        "risk_factors": ["Unable to determine risks"],
                        "support_level": current_price * 0.95,
                        "resistance_level": current_price * 1.05
                    })
            else:
                print(f"❌ API request failed: {response.text}")
                return json.dumps({
                    "price_target": current_price,
                    "confidence": 0,
                    "timeframe": "Unknown",
                    "key_factors": ["Analysis failed - API error"],
                    "risk_factors": ["Unable to determine risks"],
                    "support_level": current_price * 0.95,
                    "resistance_level": current_price * 1.05
                })
        except Exception as e:
            print(f"❌ Error in price prediction: {str(e)}")
            return json.dumps({
                "price_target": current_price,
                "confidence": 0,
                "timeframe": "Unknown",
                "key_factors": ["Analysis failed - system error"],
                "risk_factors": ["Unable to determine risks"],
                "support_level": current_price * 0.95,
                "resistance_level": current_price * 1.05
            })

def _get_pattern_analysis(self, df):
        """Get AI-powered pattern analysis"""
        print("\nMaking API call for pattern analysis...")
        
        # Format the price data as a simple string
        price_data = df[['Open', 'High', 'Low', 'Close']].tail(5)
        price_str = "\n".join([
            f"Date {idx}: O:{row['Open']:.2f} H:{row['High']:.2f} L:{row['Low']:.2f} C:{row['Close']:.2f}" 
            for idx, row in price_data.iterrows()
        ])
        
        current_price = df['Close'].iloc[-1]
        
        prompt = f"""Analyze the following price action and technical indicators to identify chart patterns:

Price Action (last 5 periods):
{price_str}

Technical Indicators:
- RSI: {df['RSI'].iloc[-1]:.2f}
- MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
- BB Upper: {df['BBU_20_2.0'].iloc[-1]:.2f}
- BB Lower: {df['BBL_20_2.0'].iloc[-1]:.2f}

Return ONLY a valid JSON object in this exact format:
{{
    "patterns": ["string"],
    "quality_score": number,
    "completion": number,
    "reliability": "string",
    "price_targets": [number],
    "key_levels": [number]
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b",
                    "messages": [
                        {"role": "system", "content": "You are a market analysis AI. Respond only with valid JSON objects, no additional text or explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Full API Response:", result)
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content'].strip()
                        print("Raw Content:", content)
                        
                        # Try to clean the content if it has markdown code blocks
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        json_content = json.loads(content)
                        required_fields = ['patterns', 'quality_score', 'completion', 'reliability']
                        if all(field in json_content for field in required_fields):
                            print("✅ Pattern analysis received and validated")
                            print(f"Detected patterns: {json_content['patterns']}")
                            return json.dumps(json_content)
                        else:
                            raise ValueError("Missing required fields in JSON response")
                    else:
                        raise ValueError("No choices in API response")
                except Exception as e:
                    print(f"❌ Error processing API response: {str(e)}")
                    print("Raw response content:", content if 'content' in locals() else "No content")
                    return json.dumps({
                        "patterns": [],
                        "quality_score": 0,
                        "completion": 0,
                        "reliability": "unknown",
                        "price_targets": [],
                        "key_levels": []
                    })
            else:
                print(f"❌ API request failed: {response.text}")
                return json.dumps({
                    "patterns": [],
                    "quality_score": 0,
                    "completion": 0,
                    "reliability": "unknown",
                    "price_targets": [],
                    "key_levels": []
                })
        except Exception as e:
            print(f"❌ Error in pattern analysis: {str(e)}")
            return json.dumps({
                "patterns": [],
                "quality_score": 0,
                "completion": 0,
                "reliability": "unknown",
                "price_targets": [],
                "key_levels": []
            })

def _get_sentiment_analysis(self, df):
        """Analyze market sentiment using price action and indicators"""
        print("\nMaking API call for sentiment analysis...")
        
        # Calculate additional indicators
        price_momentum = df['Close'].pct_change().rolling(window=5).mean().iloc[-1]
        volume_momentum = df['Volume'].pct_change().rolling(window=5).mean().iloc[-1]
        rsi_trend = df['RSI'].diff().rolling(window=3).mean().iloc[-1]
        macd_trend = df['MACD_12_26_9'].diff().rolling(window=3).mean().iloc[-1]
        
        prompt = f"""Analyze the following market data and provide a detailed sentiment analysis:

Technical Indicators:
- RSI: {df['RSI'].iloc[-1]:.2f} (Trend: {rsi_trend:.4f})
- MACD: {df['MACD_12_26_9'].iloc[-1]:.2f} (Trend: {macd_trend:.4f})
- Price Momentum: {price_momentum:.2%}
- Volume Momentum: {volume_momentum:.2%}
- Bollinger Position: {((df['Close'].iloc[-1] - df['BBL_20_2.0'].iloc[-1]) / (df['BBU_20_2.0'].iloc[-1] - df['BBL_20_2.0'].iloc[-1])):.2f}

Return ONLY a valid JSON object in this exact format:
{{
    "overall_sentiment": "string",
    "sentiment_score": number,
    "momentum_signals": ["string"],
    "reversal_signals": ["string"],
    "volume_analysis": "string",
    "strength_indicators": ["string"],
    "weakness_indicators": ["string"],
    "market_psychology": "string"
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b",
                    "messages": [
                        {"role": "system", "content": "You are a market sentiment analysis AI. For overall_sentiment use one of: ['Strongly Bullish', 'Moderately Bullish', 'Neutral', 'Moderately Bearish', 'Strongly Bearish']. Sentiment score should be from -100 to 100."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 250
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Full API Response:", result)
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content'].strip()
                        print("Raw Content:", content)
                        
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        json_content = json.loads(content)
                        required_fields = ['overall_sentiment', 'sentiment_score', 'momentum_signals', 'reversal_signals', 
                                        'volume_analysis', 'strength_indicators', 'weakness_indicators', 'market_psychology']
                        if all(field in json_content for field in required_fields):
                            print("✅ Sentiment analysis received and validated")
                            print(f"Overall Sentiment: {json_content['overall_sentiment']} (Score: {json_content['sentiment_score']})")
                            return json.dumps(json_content)
                        else:
                            raise ValueError("Missing required fields in JSON response")
                    else:
                        raise ValueError("No choices in API response")
                except Exception as e:
                    print(f"❌ Error processing API response: {str(e)}")
                    print("Raw response content:", content if 'content' in locals() else "No content")
                    return json.dumps({
                        "overall_sentiment": "Unknown",
                        "sentiment_score": 0,
                        "momentum_signals": [],
                        "reversal_signals": [],
                        "volume_analysis": "Analysis failed",
                        "strength_indicators": [],
                        "weakness_indicators": [],
                        "market_psychology": "Analysis failed"
                    })
            else:
                print(f"❌ API request failed: {response.text}")
                return json.dumps({
                    "overall_sentiment": "Unknown",
                    "sentiment_score": 0,
                    "momentum_signals": [],
                    "reversal_signals": [],
                    "volume_analysis": "Analysis failed",
                    "strength_indicators": [],
                    "weakness_indicators": [],
                    "market_psychology": "Analysis failed"
                })
        except Exception as e:
            print(f"❌ Error in sentiment analysis: {str(e)}")
            return json.dumps({
                "overall_sentiment": "Unknown",
                "sentiment_score": 0,
                "momentum_signals": [],
                "reversal_signals": [],
                "volume_analysis": "Analysis failed",
                "strength_indicators": [],
                "weakness_indicators": [],
                "market_psychology": "Analysis failed"
            })

def _get_market_context(self, df):
        """Analyze broader market context and potential scenarios"""
        print("\nMaking API call for market context analysis...")
        
        # Calculate market context metrics
        volatility_trend = df['Volatility'].diff().rolling(window=5).mean().iloc[-1]
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        prompt = f"""Analyze the following market context and provide detailed insights:

Market Context:
- Current Volatility: {df['Volatility'].iloc[-1]:.4f} (Trend: {volatility_trend:.4f})
- Volume Ratio: {volume_ratio:.2f}x average
- ATR: {df['ATR'].iloc[-1]:.2f}
- RSI: {df['RSI'].iloc[-1]:.2f}
- MACD: {df['MACD_12_26_9'].iloc[-1]:.2f}
- MACD Signal: {df['MACDs_12_26_9'].iloc[-1]:.2f}

Return ONLY a valid JSON object in this exact format:
{{
    "market_phase": "string",
    "dominant_traders": "string",
    "key_levels": {{
        "immediate_support": number,
        "immediate_resistance": number,
        "major_support": number,
        "major_resistance": number
    }},
    "volume_profile": "string",
    "volatility_state": "string",
    "potential_scenarios": [
        {{
            "scenario": "string",
            "probability": number,
            "key_triggers": ["string"]
        }}
    ],
    "risk_reward_ratio": number,
    "recommended_position_size": "string"
}}"""

        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b",
                    "messages": [
                        {"role": "system", "content": "You are a market context analysis AI. For market_phase use one of: ['Accumulation', 'Mark Up', 'Distribution', 'Mark Down', 'Re-accumulation']. For dominant_traders use one of: ['Institutional', 'Retail', 'Mixed']. Probabilities should sum to 100."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 350
                }
            )
            
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Full API Response:", result)
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content'].strip()
                        print("Raw Content:", content)
                        
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        json_content = json.loads(content)
                        required_fields = ['market_phase', 'dominant_traders', 'key_levels', 'volume_profile', 
                                        'volatility_state', 'potential_scenarios', 'risk_reward_ratio', 
                                        'recommended_position_size']
                        if all(field in json_content for field in required_fields):
                            print("✅ Market context analysis received and validated")
                            print(f"Market Phase: {json_content['market_phase']} (R/R: {json_content['risk_reward_ratio']})")
                            return json.dumps(json_content)
                        else:
                            raise ValueError("Missing required fields in JSON response")
                    else:
                        raise ValueError("No choices in API response")
                except Exception as e:
                    print(f"❌ Error processing API response: {str(e)}")
                    print("Raw response content:", content if 'content' in locals() else "No content")
                    return json.dumps({
                        "market_phase": "Unknown",
                        "dominant_traders": "Unknown",
                        "key_levels": {
                            "immediate_support": df['Close'].iloc[-1] * 0.95,
                            "immediate_resistance": df['Close'].iloc[-1] * 1.05,
                            "major_support": df['Close'].iloc[-1] * 0.90,
                            "major_resistance": df['Close'].iloc[-1] * 1.10
                        },
                        "volume_profile": "Analysis failed",
                        "volatility_state": "Unknown",
                        "potential_scenarios": [],
                        "risk_reward_ratio": 0,
                        "recommended_position_size": "Analysis failed"
                    })
            else:
                print(f"❌ API request failed: {response.text}")
                return json.dumps({
                    "market_phase": "Unknown",
                    "dominant_traders": "Unknown",
                    "key_levels": {
                        "immediate_support": df['Close'].iloc[-1] * 0.95,
                        "immediate_resistance": df['Close'].iloc[-1] * 1.05,
                        "major_support": df['Close'].iloc[-1] * 0.90,
                        "major_resistance": df['Close'].iloc[-1] * 1.10
                    },
                    "volume_profile": "Analysis failed",
                    "volatility_state": "Unknown",
                    "potential_scenarios": [],
                    "risk_reward_ratio": 0,
                    "recommended_position_size": "Analysis failed"
                })
        except Exception as e:
            print(f"❌ Error in market context analysis: {str(e)}")
            return json.dumps({
                "market_phase": "Unknown",
                "dominant_traders": "Unknown",
                "key_levels": {
                    "immediate_support": df['Close'].iloc[-1] * 0.95,
                    "immediate_resistance": df['Close'].iloc[-1] * 1.05,
                    "major_support": df['Close'].iloc[-1] * 0.90,
                    "major_resistance": df['Close'].iloc[-1] * 1.10
                },
                "volume_profile": "Analysis failed",
                "volatility_state": "Unknown",
                "potential_scenarios": [],
                "risk_reward_ratio": 0,
                "recommended_position_size": "Analysis failed"
            })

def analyze(self, symbol, timeframe='1d', period='3mo'):
        """Perform comprehensive market analysis using AI"""
        print(f"\n=== Fetching Data for {symbol} ===")
        print(f"Timeframe: {timeframe}, Period: {period}")
        
        try:
            # Fetch and prepare data
            df = self._get_data(symbol, timeframe, period)
            if df is None or len(df) < 20:  # Need at least 20 periods for indicators
                raise ValueError("Insufficient data for analysis")
            
            print("\n=== Starting Analysis ===")
            print(f"Analyzing last {min(30, len(df))} periods")
            
            # 1. Pattern Analysis
            print("\n1. Technical Pattern Analysis...")
            pattern_analysis = json.loads(self._get_pattern_analysis(df))
            
            # 2. Market Regime
            print("\n2. Market Regime Analysis...")
            regime_analysis = json.loads(self._get_market_regime(df))
            
            # 3. Price Prediction
            print("\n3. Price Prediction Analysis...")
            price_prediction = json.loads(self._get_price_prediction(df))
            
            # 4. Sentiment Analysis
            print("\n4. Market Sentiment Analysis...")
            sentiment_analysis = json.loads(self._get_sentiment_analysis(df))
            
            # 5. Market Context
            print("\n5. Market Context Analysis...")
            market_context = json.loads(self._get_market_context(df))
            
            print("\nPreparing comprehensive analysis...")
            
            # Combine all analyses into a single response
            analysis = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "current_price": df['Close'].iloc[-1],
                "technical_patterns": {
                    "detected_patterns": pattern_analysis.get("patterns", []),
                    "quality_score": pattern_analysis.get("quality_score", 0),
                    "reliability": pattern_analysis.get("reliability", "unknown")
                },
                "market_regime": {
                    "regime": regime_analysis.get("regime", "Unknown"),
                    "confidence": regime_analysis.get("confidence", 0),
                    "trend_strength": regime_analysis.get("trend_strength", 0),
                    "volatility_regime": regime_analysis.get("volatility_regime", "Unknown"),
                    "characteristics": regime_analysis.get("characteristics", [])
                },
                "price_prediction": {
                    "target": price_prediction.get("price_target", df['Close'].iloc[-1]),
                    "timeframe": price_prediction.get("timeframe", "Unknown"),
                    "confidence": price_prediction.get("confidence", 0),
                    "key_factors": price_prediction.get("key_factors", []),
                    "risk_factors": price_prediction.get("risk_factors", []),
                    "support_level": price_prediction.get("support_level", df['Close'].iloc[-1] * 0.95),
                    "resistance_level": price_prediction.get("resistance_level", df['Close'].iloc[-1] * 1.05)
                },
                "sentiment": {
                    "overall": sentiment_analysis.get("overall_sentiment", "Unknown"),
                    "score": sentiment_analysis.get("sentiment_score", 0),
                    "momentum_signals": sentiment_analysis.get("momentum_signals", []),
                    "reversal_signals": sentiment_analysis.get("reversal_signals", []),
                    "volume_analysis": sentiment_analysis.get("volume_analysis", "Unknown"),
                    "market_psychology": sentiment_analysis.get("market_psychology", "Unknown")
                },
                "market_context": {
                    "phase": market_context.get("market_phase", "Unknown"),
                    "dominant_traders": market_context.get("dominant_traders", "Unknown"),
                    "volume_profile": market_context.get("volume_profile", "Unknown"),
                    "volatility_state": market_context.get("volatility_state", "Unknown"),
                    "risk_reward_ratio": market_context.get("risk_reward_ratio", 0),
                    "position_sizing": market_context.get("recommended_position_size", "Unknown"),
                    "key_levels": market_context.get("key_levels", {
                        "immediate_support": df['Close'].iloc[-1] * 0.95,
                        "immediate_resistance": df['Close'].iloc[-1] * 1.05,
                        "major_support": df['Close'].iloc[-1] * 0.90,
                        "major_resistance": df['Close'].iloc[-1] * 1.10
                    }),
                    "scenarios": market_context.get("potential_scenarios", [])
                },
                "technical_indicators": {
                    "rsi": df['RSI'].iloc[-1],
                    "macd": df['MACD_12_26_9'].iloc[-1],
                    "macd_signal": df['MACDs_12_26_9'].iloc[-1],
                    "volatility": df['Volatility'].iloc[-1],
                    "atr": df['ATR'].iloc[-1]
                }
            }
            
            print("✅ Analysis complete")
            return analysis, df
            
        except Exception as e:
            print(f"❌ Error in analysis: {str(e)}")
            return None, None 