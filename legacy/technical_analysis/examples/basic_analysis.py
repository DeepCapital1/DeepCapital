import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pattern_detector import PatternDetector
import pandas as pd
from datetime import datetime, timedelta
import plotly.io as pio

def run_example():
    """Run a basic example of pattern detection"""
    
    print("🚀 Starting Technical Analysis Pattern Detection Example")
    
    # Initialize the detector
    print("\n1. Initializing Pattern Detector...")
    detector = PatternDetector()
    
    # Define symbols to analyze
    symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD']
    timeframes = ['1d', '1h']
    
    for symbol in symbols:
        print(f"\n📊 Analyzing {symbol}")
        
        for timeframe in timeframes:
            print(f"\n⏰ Timeframe: {timeframe}")
            
            try:
                # Fetch data
                print("Fetching historical data...")
                df = detector.fetch_data(symbol, interval=timeframe, period='3mo')
                
                if df is not None and not df.empty:
                    # Add technical indicators
                    print("Adding technical indicators...")
                    df = detector.add_technical_indicators(df)
                    
                    # Detect patterns
                    print("Detecting patterns...")
                    patterns = detector.detect_patterns(df)
                    
                    if patterns:
                        print("\nResults:")
                        print("--------")
                        
                        # Display patterns
                        if patterns.get('patterns'):
                            print("\n🎯 Identified Patterns:")
                            for pattern in patterns['patterns']:
                                print(f"- {pattern}")
                        
                        # Display entry/exit points
                        if patterns.get('entry_exit'):
                            print("\n📍 Entry/Exit Points:")
                            entry_exit = patterns['entry_exit']
                            if 'entry' in entry_exit:
                                print(f"Entry: {entry_exit['entry']}")
                            if 'exit' in entry_exit:
                                print(f"Exit: {entry_exit['exit']}")
                        
                        # Display support/resistance
                        if patterns.get('support_resistance'):
                            print("\n📊 Support & Resistance Levels:")
                            for level in patterns['support_resistance']:
                                print(f"- {level}")
                        
                        # Display risk assessment
                        if patterns.get('risk_assessment'):
                            print(f"\n⚠️ Risk Assessment:")
                            print(patterns['risk_assessment'])
                        
                        # Display price target
                        if patterns.get('price_target'):
                            print(f"\n🎯 Price Target:")
                            print(patterns['price_target'])
                        
                        # Display success rate
                        if patterns.get('success_rate'):
                            print(f"\n📈 Success Rate:")
                            print(patterns['success_rate'])
                        
                        # Generate and save plot
                        print("\n📈 Generating chart...")
                        fig = detector.plot_pattern(df, patterns)
                        
                        # Create output directory if it doesn't exist
                        output_dir = 'output'
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        # Save the plot
                        filename = f"{output_dir}/{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                        pio.write_html(fig, filename)
                        print(f"Chart saved to: {filename}")
                        
                    else:
                        print("No clear patterns detected in the current timeframe.")
                
                else:
                    print("Failed to fetch data. Please check the symbol and try again.")
                    
            except Exception as e:
                print(f"Error analyzing {symbol} on {timeframe}: {str(e)}")
                continue
            
            print("\n" + "="*50)

if __name__ == "__main__":
    run_example() 