import os
import pandas as pd
from datetime import datetime, timedelta
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import asyncio
import platform
import subprocess

class RequestQueue:
    def __init__(self):
        self.queue = []
        self.processing = False

    async def add(self, request):
        """Add a request to the queue and process it"""
        return await self._add_to_queue(request)

    async def _add_to_queue(self, request):
        """Helper method to add request to queue"""
        future = asyncio.Future()
        self.queue.append((request, future))
        await self._process_queue()
        return await future

    async def _process_queue(self):
        """Process queued requests with rate limiting"""
        if self.processing or not self.queue:
            return
            
        self.processing = True
        
        while self.queue:
            request, future = self.queue[0]
            try:
                result = await request()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
                await self._exponential_backoff(len(self.queue))
            
            self.queue.pop(0)
            await self._random_delay()
            
        self.processing = False

    async def _exponential_backoff(self, retry_count):
        """Implement exponential backoff"""
        delay = 2 ** retry_count
        await asyncio.sleep(delay)

    async def _random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(1.5, 3.5)
        await asyncio.sleep(delay)

class TwitterScraper:
    def __init__(self):
        self.driver = None
        self.request_queue = RequestQueue()
        self.cookies = None
        
    def init_driver(self):
        """Initialize Firefox driver with appropriate options"""
        try:
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--width=1920')
            firefox_options.add_argument('--height=1080')
            
            # Initialize the driver
            self.driver = webdriver.Firefox(options=firefox_options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize Firefox driver: {str(e)}")
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False

    async def login(self, username, password, email=None, twofa_secret=None):
        """Login to Twitter using browser automation"""
        if not self.driver and not self.init_driver():
            raise Exception("Failed to initialize Firefox driver")
            
        try:
            print("Navigating to Twitter login page...")
            self.driver.get('https://twitter.com/login')
            time.sleep(3)  # Increased wait time
            
            print("Entering username...")
            username_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)
            
            print("Clicking Next button...")
            next_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next')]"))
            )
            next_button.click()
            time.sleep(2)
            
            print("Entering password...")
            password_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            print("Clicking Login button...")
            login_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Log in')]"))
            )
            login_button.click()
            time.sleep(3)
            
            # Check if 2FA is requested
            try:
                twofa_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "code"))
                )
                if twofa_input and twofa_secret:
                    print("Handling 2FA...")
                    code = self._generate_2fa_code(twofa_secret)
                    twofa_input.clear()
                    twofa_input.send_keys(code)
                    time.sleep(1)
                    
                    verify_button = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Verify')]"))
                    )
                    verify_button.click()
                    time.sleep(2)
            except:
                # 2FA not requested, continue with login
                pass
            
            print("Waiting for successful login...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
            )
            
            print("Login successful!")
            self.cookies = self.driver.get_cookies()
            return True
            
        except Exception as e:
            print(f"Login failed with error: {str(e)}")
            print("Current URL:", self.driver.current_url)
            print("Page source:", self.driver.page_source[:500])  # Print first 500 chars of page source
            if self.driver:
                self.driver.save_screenshot('login_error.png')
            return False

    async def is_logged_in(self):
        """Check if currently logged in to Twitter"""
        if not self.driver:
            return False
            
        try:
            self.driver.get('https://twitter.com/home')
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
            )
            return True
        except:
            return False

    async def search_tweets(self, query, max_results=100):
        """Search for tweets matching query"""
        tweets = []
        print(f"\nSearching Twitter for: {query}")
        
        try:
            search_url = f'https://twitter.com/search?q={query}&src=typed_query&f=live'
            print(f"Navigating to search URL: {search_url}")
            self.driver.get(search_url)
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            tweet_count = 0
            scroll_count = 0
            max_scrolls = 10  # Limit scrolling to avoid infinite loops
            
            while tweet_count < max_results and scroll_count < max_scrolls:
                print(f"\nScroll {scroll_count + 1}/{max_scrolls}")
                # Find tweet elements
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                print(f"Found {len(tweet_elements)} tweets on current page")
                
                for tweet in tweet_elements[tweet_count:]:
                    try:
                        # Extract tweet data
                        text = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']").text
                        username = tweet.find_element(By.CSS_SELECTOR, "[data-testid='User-Name']").text
                        timestamp = tweet.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                        
                        # Get engagement metrics
                        metrics = tweet.find_elements(By.CSS_SELECTOR, "[data-testid$='-count']")
                        likes = int(metrics[0].text) if metrics else 0
                        retweets = int(metrics[1].text) if len(metrics) > 1 else 0
                        replies = int(metrics[2].text) if len(metrics) > 2 else 0
                        
                        print(f"\nExtracted Tweet {tweet_count + 1}:")
                        print(f"Username: {username}")
                        print(f"Text: {text[:100]}...")  # Print first 100 chars
                        print(f"Engagement: {likes} likes, {retweets} retweets, {replies} replies")
                        
                        tweets.append({
                            'text': text,
                            'username': username,
                            'timestamp': timestamp,
                            'likes': likes,
                            'retweets': retweets,
                            'replies': replies
                        })
                        
                        tweet_count += 1
                        if tweet_count >= max_results:
                            print("\nReached maximum tweet count")
                            break
                            
                    except Exception as e:
                        print(f"Error extracting tweet data: {str(e)}")
                        continue
                
                # Scroll down
                print("Scrolling down...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("Reached end of page")
                    break
                    
                last_height = new_height
                scroll_count += 1
                
        except Exception as e:
            print(f"Error searching tweets: {str(e)}")
            
        print(f"\nTotal tweets collected: {len(tweets)}")
        return tweets

class DataCollector:
    def __init__(self):
        load_dotenv()
        self.twitter_scraper = TwitterScraper()
        
    async def init(self):
        """Initialize the Twitter scraper with login"""
        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')
        twofa_secret = os.getenv('TWITTER_2FA_SECRET')
        
        if not username or not password:
            raise ValueError("Twitter credentials not configured")
            
        success = await self.twitter_scraper.login(username, password, twofa_secret=twofa_secret)
        if not success:
            raise Exception("Failed to login to Twitter")
        
    async def get_twitter_data(self, ticker, hours_back=24):
        """Collect Twitter data for a specific crypto ticker"""
        print(f"\nCollecting Twitter data for {ticker} from past {hours_back} hours")
        search_query = f"{ticker} -is:retweet lang:en"
        tweets = await self.twitter_scraper.search_tweets(search_query, max_results=50)  # Reduced from 100
        
        # Filter tweets by time
        cutoff_time = datetime.utcnow().replace(tzinfo=None)
        filtered_tweets = [
            tweet for tweet in tweets 
            if datetime.fromisoformat(tweet['timestamp'].replace('Z', '')).replace(tzinfo=None) > cutoff_time - timedelta(hours=hours_back)
        ]
        
        print(f"Found {len(filtered_tweets)} tweets within time range")
        return pd.DataFrame(filtered_tweets)
    
    async def aggregate_data(self, ticker, hours_back=24):
        """Aggregate Twitter data for analysis"""
        print(f"\nAggregating data for {ticker}")
        twitter_data = await self.get_twitter_data(ticker, hours_back)
        
        all_texts = []
        
        # Process Twitter data
        if not twitter_data.empty:
            print("\nProcessing Twitter data...")
            # Sort by engagement (likes + retweets + replies)
            twitter_data['engagement'] = (twitter_data['likes'] + 
                                        twitter_data['retweets'] + 
                                        twitter_data['replies'])
            twitter_data = twitter_data.sort_values('engagement', ascending=False)
            
            # Get top 15 most engaged tweets
            top_tweets = twitter_data.head(15)  # Reduced from 20
            print(f"Selected top {len(top_tweets)} tweets by engagement")
            
            all_texts.extend([{
                'text': text,
                'source': 'twitter',
                'engagement': engagement
            } for text, engagement in zip(top_tweets['text'], 
                                        top_tweets['engagement'])])
        else:
            print("No Twitter data found")
        
        print(f"\nTotal sources for analysis: {len(all_texts)}")
        return pd.DataFrame(all_texts) 