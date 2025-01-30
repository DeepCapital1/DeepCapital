import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from pattern_detector import PatternDetector

class TestPatternDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.detector = PatternDetector()
        
        # Create sample price data with realistic movements
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        base_price = 100
        prices = []
        for i in range(len(dates)):
            # Add some random movement
            change = np.random.normal(0, 2)  # Random change with mean 0 and std 2
            base_price += change
            
            # Create OHLC data
            high = base_price + abs(np.random.normal(0, 1))
            low = base_price - abs(np.random.normal(0, 1))
            open_price = np.random.uniform(low, high)
            close = np.random.uniform(low, high)
            volume = np.random.randint(500000, 1500000)
            
            prices.append([open_price, high, low, close, volume])
        
        cls.sample_data = pd.DataFrame(prices, index=dates,
                                     columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Create a head and shoulders pattern
        # Left shoulder
        cls.sample_data.loc['2024-01-10':'2024-01-12', 'Close'] = [105, 110, 107]
        # Head
        cls.sample_data.loc['2024-01-13':'2024-01-15', 'Close'] = [108, 115, 110]
        # Right shoulder
        cls.sample_data.loc['2024-01-16':'2024-01-18', 'Close'] = [105, 108, 102]
        
        # Update High and Low values for the pattern
        pattern_dates = pd.date_range(start='2024-01-10', end='2024-01-18', freq='D')
        for date in pattern_dates:
            cls.sample_data.loc[date, 'High'] = cls.sample_data.loc[date, 'Close'] + 2
            cls.sample_data.loc[date, 'Low'] = cls.sample_data.loc[date, 'Close'] - 2
            cls.sample_data.loc[date, 'Open'] = cls.sample_data.loc[date, 'Close'] - 1
    
    def test_initialization(self):
        """Test if the detector initializes correctly"""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.api_key)
        self.assertIsInstance(self.detector.indicators, dict)
    
    def test_fetch_data(self):
        """Test data fetching functionality"""
        df = self.detector.fetch_data('BTC-USD', interval='1d', period='1mo')
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']))
    
    def test_technical_indicators(self):
        """Test technical indicator calculations"""
        df = self.detector.add_technical_indicators(self.sample_data)
        
        # Check if indicators are added
        self.assertTrue('RSI' in df.columns)
        self.assertTrue('MACD_12_26_9' in df.columns)
        self.assertTrue('BBU_20_2.0' in df.columns)
        self.assertTrue('BBL_20_2.0' in df.columns)
        self.assertTrue('ATR' in df.columns)
        
        # Check if indicators have valid values
        self.assertTrue(df['RSI'].notna().any())
        self.assertTrue(df['MACD_12_26_9'].notna().any())
        self.assertTrue(df['ATR'].notna().any())
    
    def test_pattern_detection(self):
        """Test pattern detection functionality"""
        # Add technical indicators first
        df = self.detector.add_technical_indicators(self.sample_data)
        
        # Detect patterns
        patterns = self.detector.detect_patterns(df)
        
        # Check if patterns are detected
        self.assertIsNotNone(patterns)
        self.assertIsInstance(patterns, dict)
        
        # Check if all required fields are present
        required_fields = ['patterns', 'support_resistance', 'entry_exit', 
                         'risk_assessment', 'price_target', 'timeframe', 'success_rate']
        for field in required_fields:
            self.assertIn(field, patterns)
    
    def test_plot_generation(self):
        """Test chart plotting functionality"""
        # Add technical indicators first
        df = self.detector.add_technical_indicators(self.sample_data)
        
        # Create sample pattern info
        pattern_info = {
            'patterns': ['Head and Shoulders'],
            'support_resistance': [95, 115],
            'entry_exit': {'entry': '100', 'exit': '110'},
            'risk_assessment': 'Medium risk',
            'price_target': '120',
            'timeframe': 'Short-term',
            'success_rate': '75%'
        }
        
        # Generate plot
        fig = self.detector.plot_pattern(df, pattern_info)
        self.assertIsNotNone(fig)
        
        # Check if the figure has the correct traces
        trace_names = [trace.name for trace in fig.data]
        self.assertIn('Price', trace_names)
        self.assertIn('BB Upper', trace_names)
        self.assertIn('BB Lower', trace_names)
    
    def test_analysis_prompt(self):
        """Test analysis prompt generation"""
        df = self.detector.add_technical_indicators(self.sample_data)
        prompt = self.detector._create_analysis_prompt(df)
        
        # Check if prompt contains all required sections
        self.assertIn('Price Action:', prompt)
        self.assertIn('Technical Indicators:', prompt)
        self.assertIn('RSI:', prompt)
        self.assertIn('MACD:', prompt)
        self.assertIn('BB Upper:', prompt)
        self.assertIn('BB Lower:', prompt)
        self.assertIn('ATR:', prompt)
    
    def test_parse_analysis(self):
        """Test analysis parsing functionality"""
        # Test with JSON format
        json_analysis = '''
        {
            "patterns": ["Head and Shoulders"],
            "support_resistance": [95, 115],
            "entry_exit": {"entry": "100", "exit": "110"},
            "risk_assessment": "Medium risk",
            "price_target": "120",
            "timeframe": "Short-term",
            "success_rate": "75%"
        }
        '''
        result = self.detector._parse_analysis(json_analysis)
        self.assertIsInstance(result, dict)
        self.assertIn('patterns', result)
        
        # Test with text format
        text_analysis = '''
        Pattern: Head and Shoulders
        Support: 95
        Resistance: 115
        Entry Point: 100
        Exit Point: 110
        Risk Assessment: Medium risk
        Price Target: 120
        Timeframe: Short-term
        Success Rate: 75%
        '''
        result = self.detector._parse_analysis(text_analysis)
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result['patterns']) > 0)

def run_tests():
    """Run the test suite"""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests() 