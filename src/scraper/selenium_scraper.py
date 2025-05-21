from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import logging
import os

class SeleniumScraper:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)    
        def initialize_driver(self):
            """Initialize the Chrome webdriver with appropriate options"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Check if running in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            # In GitHub Actions, use the pre-installed Chrome
            self.logger.info("Running in GitHub Actions environment")
            options.binary_location = "/usr/bin/google-chrome"
            self.driver = webdriver.Chrome(options=options)
        else:
            # In local environment, use webdriver-manager
            self.logger.info("Running in local environment")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
        self.driver.maximize_window()
        self.logger.info("Chrome driver initialized successfully")

    def initialize_driver(self):
        """Initialize the Chrome WebDriver with appropriate options"""
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def scrape_tournament_data(self):
        """Scrape tournament data from SuperPlayerAuction.com"""
        try:
            self.logger.info("Starting to scrape tournament data")
            self.driver.get("https://www.superplayerauction.com/upcoming-auction/")
            
            # Wait for the initial page load
            self.logger.info("Waiting for page to load...")
            time.sleep(5)
            
            # Scroll down the page to ensure all auction cards load
            self.logger.info("Scrolling to load all auction cards...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Scroll in smaller increments to ensure all cards load
            for i in range(1, 11):
                scroll_point = int(last_height * (i / 10))
                self.driver.execute_script(f"window.scrollTo(0, {scroll_point});")
                time.sleep(1)  # Wait for content to load after each scroll
            
            # Scroll back to top to start processing
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)  # Wait after scrolling up
            
            # Take a screenshot for debugging
            screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            screenshot_path = os.path.join(screenshots_dir, f"page_loaded_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Saved page screenshot to {screenshot_path}")
            
            try:
                # Look for the auction grid using the correct class name
                self.logger.info("Looking for auction cards...")
                
                wait = WebDriverWait(self.driver, 15)
                auction_grid = wait.until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "TodayAuctions_auctions-grid__rwzk6")))
                
                # Find all auction cards within the grid using the correct class name
                auction_cards = auction_grid.find_elements(By.CLASS_NAME, "TodayAuctions_auction-card__GKW_1")
                self.logger.info(f"Found {len(auction_cards)} auction cards")
                
                # List to store scraped data
                tournament_data = []
                
                # Extract data from each auction card
                for idx, card in enumerate(auction_cards):
                    try:
                        # Scroll the card into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                        time.sleep(0.5)  # Small pause after scrolling
                        
                        # Get tournament name
                        tournament_name = card.find_element(By.CLASS_NAME, "TodayAuctions_auction-title__mZovr").text.strip()
                        
                        # Get location and date from the info items
                        info_items = card.find_elements(By.CLASS_NAME, "TodayAuctions_info-item__xrFwU")
                        
                        location = "Unknown"
                        event_date = ""
                        phone = ""
                        email = ""
                        facebook = ""
                        organizer = ""
                        
                        # Process each info item to get location and date
                        for item in info_items:
                            try:
                                svg_element = item.find_element(By.TAG_NAME, "svg")
                                span_text = item.find_element(By.TAG_NAME, "span").text.strip()
                                
                                # Check icon type and assign data accordingly
                                if "map-pin" in svg_element.get_attribute("class"):
                                    location = span_text
                                elif "calendar" in svg_element.get_attribute("class"):
                                    event_date = span_text
                                elif "user" in svg_element.get_attribute("class"):
                                    organizer = span_text
                                elif "phone" in svg_element.get_attribute("class"):
                                    phone = span_text
                                elif "mail" in svg_element.get_attribute("class"):
                                    email = span_text
                            except:
                                continue
                        
                        # Try to find Facebook link if available
                        try:
                            social_links = card.find_elements(By.CLASS_NAME, "TodayAuctions_social-link__zFCc5")
                            for link in social_links:
                                href = link.get_attribute("href")
                                if "facebook" in href:
                                    facebook = href
                                    break
                        except:
                            pass
                        
                        # Format the date
                        try:
                            date_obj = datetime.strptime(event_date, "%d-%m-%Y")
                            formatted_date = date_obj.strftime("%d %b")  # e.g., "15 May"
                        except:
                            formatted_date = event_date
                        
                        # Get today's date in the format "20 May"
                        today_date = datetime.now().strftime("%d %b")
                        
                        # Remove "Players/Team" from organizer if it exists
                        if organizer and "Players/Team" in organizer:
                            organizer = organizer.split("Players/Team")[0].strip()
                        
                        # Create a dictionary for this tournament with the exact column names from Excel
                        tournament = {
                            "Tournament Name": tournament_name,
                            "Location": location,
                            "Organizer Name": organizer,
                            "Auction Date": formatted_date,  # This was previously "Date Added"
                            "Date Added": today_date,        # Add today's date
                            "Transferred to Phone Sheet": "",
                            "Phone Number/email": phone if phone else email,
                            "Email": email,
                            "Facebook Link": facebook
                        }
                        
                        tournament_data.append(tournament)
                        self.logger.info(f"Scraped tournament {idx+1}: {tournament_name}")
                        
                    except Exception as e:
                        self.logger.error(f"Error extracting data from card #{idx+1}: {e}")
                        # Take screenshot of problematic card
                        card_screenshot = os.path.join(screenshots_dir, f"error_card_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                        self.driver.save_screenshot(card_screenshot)
                        continue
                
                return tournament_data
                
            except TimeoutException:
                self.logger.error("Timeout waiting for auction cards to load")
                error_screenshot = os.path.join(screenshots_dir, f"timeout_error_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                self.driver.save_screenshot(error_screenshot)
                return []
                
            except NoSuchElementException as e:
                self.logger.error(f"Could not find element: {e}")
                error_screenshot = os.path.join(screenshots_dir, f"element_not_found_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                self.driver.save_screenshot(error_screenshot)
                return []
                
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return []
            
        finally:
            # Don't close the driver here, it will be closed in the main script
            pass

    def close_driver(self):
        """Close the Selenium webdriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Chrome driver closed")