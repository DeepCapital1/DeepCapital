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
from webdriver_manager.firefox import GeckoDriverManager
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
            print("Setting up Firefox options...")
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--width=1920')
            firefox_options.add_argument('--height=1080')
            firefox_options.add_argument('--disable-gpu')
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference('useAutomationExtension', False)
            
            print("Installing GeckoDriver...")
            service = Service(GeckoDriverManager().install())
            
            print("Initializing Firefox driver...")
            # self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.driver = webdriver.Firefox(options=firefox_options)
            # Set various timeouts
            print("Configuring timeouts...")
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("Firefox driver initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Firefox driver: {str(e)}")
            print("Error details:", str(e.__class__.__name__))
            import traceback
            print("Traceback:", traceback.format_exc())
            
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
            self.driver.get('https://x.com/login')
            time.sleep(5)  # Increased wait for initial page load
            
            print("Entering username...")
            # Try multiple possible selectors for username field
            username_selectors = [
                "input[autocomplete='username']",
                "input[name='text']",
                "input[autocomplete='email']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_input.is_displayed():
                        break
                except:
                    continue
            
            if not username_input:
                raise Exception("Could not find username input field")
                
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(2)
            
            print("Clicking Next button...")
            # Try multiple possible selectors for next button
            next_button_selectors = [
                "//div[@role='button'][.//span[text()='Next']]",
                "//span[text()='Next']/..",
                "//div[contains(@class, 'next')]"
            ]
            
            next_button = None
            for selector in next_button_selectors:
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if next_button.is_displayed():
                        break
                except:
                    continue
            
            if not next_button:
                raise Exception("Could not find next button")
                
            next_button.click()
            time.sleep(3)
            
            # Check if email verification is requested
            try:
                email_input = None
                email_selectors = [
                    "input[autocomplete='email']",
                    "input[name='text']",
                    "input[type='text']"
                ]
                
                for selector in email_selectors:
                    try:
                        email_input = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if email_input.is_displayed():
                            break
                    except:
                        continue
                
                if email_input:
                    print("Email verification requested...")
                    if not email:
                        raise Exception("Email verification required but no email provided")
                    
                    email_input.clear()
                    email_input.send_keys(email)
                    time.sleep(1)
                    
                    # Click next after entering email
                    next_button = None
                    for selector in next_button_selectors:
                        try:
                            next_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            if next_button.is_displayed():
                                break
                        except:
                            continue
                    
                    if next_button:
                        next_button.click()
                        time.sleep(3)
                    else:
                        raise Exception("Could not find next button after email input")
            except Exception as e:
                if "Email verification required" in str(e):
                    raise
                # If no email verification needed, continue to password
                pass
            
            print("Entering password...")
            # Try multiple possible selectors for password field
            password_selectors = [
                "input[autocomplete='current-password']",
                "input[name='password']",
                "input[type='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if password_input.is_displayed():
                        break
                except:
                    continue
            
            if not password_input:
                # Take a screenshot and save page source for debugging
                self.driver.save_screenshot('password_field_error.png')
                with open('password_field_debug.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                raise Exception("Could not find password input field")
                
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(2)
            
            print("Clicking Login button...")
            # Try multiple possible selectors for login button
            login_button_selectors = [
                "//div[@role='button'][.//span[text()='Log in']]",
                "//span[text()='Log in']/..",
                "//div[contains(@data-testid, 'LoginButton')]"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if login_button.is_displayed():
                        break
                except:
                    continue
            
            if not login_button:
                raise Exception("Could not find login button")
                
            login_button.click()
            time.sleep(5)  # Increased wait after login
            
            # Check if 2FA is requested
            try:
                twofa_selectors = [
                    "input[autocomplete='one-time-code']",
                    "input[name='text']",
                    "input[inputmode='numeric']"
                ]
                
                twofa_input = None
                for selector in twofa_selectors:
                    try:
                        twofa_input = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if twofa_input.is_displayed():
                            break
                    except:
                        continue
                
                if twofa_input and twofa_secret:
                    print("Handling 2FA...")
                    code = self._generate_2fa_code(twofa_secret)
                    twofa_input.clear()
                    twofa_input.send_keys(code)
                    time.sleep(2)
                    
                    verify_button_selectors = [
                        "//div[@role='button'][.//span[text()='Verify']]",
                        "//span[text()='Verify']/..",
                        "//div[contains(@data-testid, 'VerifyButton')]"
                    ]
                    
                    verify_button = None
                    for selector in verify_button_selectors:
                        try:
                            verify_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            if verify_button.is_displayed():
                                break
                        except:
                            continue
                    
                    if verify_button:
                        verify_button.click()
                        time.sleep(3)
            except:
                # 2FA not requested, continue with login
                pass
            
            print("Waiting for successful login...")
            # Try multiple success indicators
            success_selectors = [
                "div[data-testid='primaryColumn']",
                "div[data-testid='AppTabBar_Home_Link']",
                "a[aria-label='Home']"
            ]
            
            success_element = None
            for selector in success_selectors:
                try:
                    success_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if success_element.is_displayed():
                        break
                except:
                    continue
            
            if not success_element:
                raise Exception("Could not verify successful login")
            
            print("Login successful!")
            self.cookies = self.driver.get_cookies()
            return True
            
        except Exception as e:
            print(f"Login failed with error: {str(e)}")
            print("Current URL:", self.driver.current_url)
            print("Page source:", self.driver.page_source[:1000])  # Print more of the page source
            if self.driver:
                self.driver.save_screenshot('login_error.png')
                # Save extended debug info
                with open('login_debug.txt', 'w') as f:
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"URL: {self.driver.current_url}\n")
                    f.write(f"Page source:\n{self.driver.page_source}")
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

    async def search_tweets(self, query, max_results=100, progress_callback=None):
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
        if tweets:
            progress_callback(f"Collected {len(tweets)} tweets from the past {max_results} hours")
        return tweets

class DataCollector:
    def __init__(self):
        load_dotenv()
        self.twitter_scraper = TwitterScraper()
        
    async def init(self):
        """Initialize the Twitter scraper with login"""
        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')
        email = os.getenv('TWITTER_EMAIL')  # Add email from env
        twofa_secret = os.getenv('TWITTER_2FA_SECRET')
        
        if not username or not password:
            raise ValueError("Twitter credentials not configured")
            
        if not email:
            print("Warning: TWITTER_EMAIL not set in .env file. This might be required for login.")
            
        success = await self.twitter_scraper.login(
            username=username,
            password=password,
            email=email,
            twofa_secret=twofa_secret
        )
        if not success:
            raise Exception("Failed to login to Twitter")
        
    async def get_twitter_data(self, ticker, hours_back=24, max_tweets=50, progress_callback=None):
        """
        Collect Twitter data for a specific crypto ticker
        
        Args:
            ticker (str): The cryptocurrency ticker to analyze
            hours_back (int): Number of hours of historical data to analyze
            max_tweets (int): Maximum number of tweets to collect (10-100)
            progress_callback (callable): Function to call with progress updates
        """
        if progress_callback is None:
            progress_callback = lambda x: None
            
        print(f"\nCollecting Twitter data for {ticker} from past {hours_back} hours")
        
        # Enhanced search query:
        # - Include both $ and # versions of the ticker
        # - Filter out retweets and replies
        # - Only English tweets
        # - Only from verified accounts or accounts with min_followers
        ticker_clean = ticker.replace('$', '').replace('#', '')
        # search_query = f"(${ticker_clean} OR #{ticker_clean}) min_followers:1000 -is:retweet -is:reply lang:en"
        search_query = f"{ticker} -is:retweet lang:en"
        print(f"Using search query: {search_query}")
        
        tweets = await self.twitter_scraper.search_tweets(search_query, max_results=max_tweets, progress_callback=progress_callback)
        
        # Filter tweets by time
        cutoff_time = datetime.utcnow().replace(tzinfo=None)
        filtered_tweets = [
            tweet for tweet in tweets 
            if datetime.fromisoformat(tweet['timestamp'].replace('Z', '')).replace(tzinfo=None) > cutoff_time - timedelta(hours=hours_back)
        ]
        
        print(f"Found {len(filtered_tweets)} tweets within time range")
        if filtered_tweets:
            progress_callback(f"Collected {len(filtered_tweets)} tweets from the past {hours_back} hours")
        
        return pd.DataFrame(filtered_tweets)
    
    async def aggregate_data(self, ticker, hours_back=24, max_tweets=50, progress_callback=None):
        """
        Aggregate Twitter data for analysis
        
        Args:
            ticker (str): The cryptocurrency ticker to analyze
            hours_back (int): Number of hours of historical data to analyze
            max_tweets (int): Maximum number of tweets to collect (10-100)
            progress_callback (callable): Function to call with progress updates
        """
        if progress_callback is None:
            progress_callback = lambda x: None
            
        print(f"\nAggregating data for {ticker}")
        twitter_data = await self.get_twitter_data(ticker, hours_back, max_tweets)
        all_texts = []
        
        # Process Twitter data
        if not twitter_data.empty:
            print("\nProcessing Twitter data...")
            # Sort by engagement (likes + retweets + replies)
            twitter_data['engagement'] = (twitter_data['likes'] + 
                                        twitter_data['retweets'] + 
                                        twitter_data['replies'])
            twitter_data = twitter_data.sort_values('engagement', ascending=False)
            
            # Get top tweets by engagement
            top_tweet_count = max(10, min(max_tweets // 3, 15))
            top_tweets = twitter_data.head(top_tweet_count)
            print(f"Selected top {len(top_tweets)} tweets by engagement")
            progress_callback(f"Selected top {len(top_tweets)} most engaged tweets for analysis")
            
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