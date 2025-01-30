# Crypto Sentiment Analyzer Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [API Configuration](#api-configuration)
- [Running the Application](#running-the-application)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip (Python package installer)
- Git
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space

### Required API Keys
- OpenRouter API key (for DeepSeek AI integration)
- Optional: Twitter API credentials (for social sentiment analysis)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/DeepCapital1/DeepCapital.git
cd DeepCapital
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

The requirements.txt includes:
```
pandas>=1.5.0
numpy>=1.21.0
yfinance>=0.2.0
pandas-ta>=0.3.0
plotly>=5.0.0
streamlit>=1.20.0
python-dotenv>=0.19.0
scikit-learn>=1.0.0
requests>=2.28.0
```

## Environment Setup

### 1. Create Environment File
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

### 2. Configure Environment Variables
Edit the `.env` file with your API credentials:
```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional - Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
```

## API Configuration

### OpenRouter API Setup
1. Visit [OpenRouter](https://openrouter.ai/)
2. Create an account and obtain API key
3. Add the API key to your `.env` file

### Twitter API Setup (Optional)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and app
3. Generate API keys and tokens
4. Add credentials to your `.env` file

## Running the Application

### 1. Start the Streamlit App
```bash
streamlit run src/app.py
```

### 2. Access the Web Interface
- Open your browser
- Navigate to `http://localhost:8501`
- Default port is 8501 unless specified otherwise

### 3. Verify Installation
- Check the connection status in the sidebar
- Test API connectivity using the "Test API" button
- Verify data fetching with a sample symbol (e.g., BTC-USD)

## Development Setup

### Setting Up Development Environment

1. **Install Development Dependencies**
```bash
pip install -r requirements-dev.txt
```

2. **Install Pre-commit Hooks**
```bash
pre-commit install
```

3. **Configure IDE**
- VSCode settings are provided in `.vscode/settings.json`
- Python path should point to your virtual environment
- Enable linting and formatting extensions

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_pattern_detector.py

# Run with coverage report
python -m pytest --cov=src tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 100 characters
- Use type hints for function parameters

## Troubleshooting

### Common Issues

1. **API Key Issues**
```
Error: OpenRouter API key not found
Solution: Verify OPENROUTER_API_KEY in .env file
```

2. **Package Installation Errors**
```
Error: Module not found
Solution: Activate virtual environment and reinstall requirements
```

3. **Data Fetching Issues**
```
Error: No data found for symbol
Solution: Verify symbol format (e.g., BTC-USD) and internet connection
```

### Environment Issues

1. **Virtual Environment**
```bash
# If venv activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If venv activation fails on Linux/MacOS
chmod +x venv/bin/activate
```

2. **Port Conflicts**
```bash
# Change Streamlit port
streamlit run src/app.py --server.port 8502
```

### Getting Help

1. **Check Logs**
- Application logs are in `logs/app.log`
- Error details are printed to console
- Check Streamlit output for runtime errors

2. **Update Dependencies**
```bash
pip install --upgrade -r requirements.txt
```

3. **Clean Installation**
```bash
# Remove virtual environment
rm -rf venv/

# Remove cached files
find . -type d -name "__pycache__" -exec rm -r {} +

# Reinstall everything
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Additional Resources

- [API Documentation](./api.md)
- [Usage Guide](./usage.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

## Support

If you encounter any issues not covered in this guide:
1. Check the [GitHub Issues](https://github.com/DeepCapital1/DeepCapital/issues)
2. Review the troubleshooting section
3. Create a new issue with:
   - Detailed error description
   - Steps to reproduce
   - Environment information
   - Relevant logs
