import sys
import os
import json
import time
from scraper.selenium_scraper import SeleniumScraper
from excel.graph_api import GraphAPI
from utils.config import load_config
from utils.logger import Logger

def main():
    # Initialize logger
    logger = Logger()
    logger.setup_logger()
    logger.log_info("Starting Super Player Auction scraper")
    
    # Load configuration settings
    config = load_config()
    if not config.get("credentials"):
        logger.log_error("Failed to load credentials. Please check id.txt file.")
        sys.exit(1)
    
    try:
        # Initialize the Selenium scraper
        logger.log_info("Initializing Selenium scraper")
        scraper = SeleniumScraper()
        scraper.initialize_driver()

        # Scrape tournament data
        logger.log_info("Scraping tournament data")
        tournament_data = scraper.scrape_tournament_data()
        
        if not tournament_data:
            logger.log_warning("No tournament data found")
        else:
            logger.log_info(f"Successfully scraped {len(tournament_data)} tournaments")
            
            # Save scraped data to a local file for backup
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            data_file = os.path.join(data_dir, f"tournament_data_{timestamp}.json")
            
            with open(data_file, 'w') as f:
                json.dump(tournament_data, f, indent=4)
                
            logger.log_info(f"Saved scraped data to {data_file}")

            # Initialize Graph API for Excel update
            logger.log_info("Initializing Graph API")
            graph_api = GraphAPI(config.get("credentials"))
            
            # Authenticate with Microsoft Graph API
            logger.log_info("Authenticating with Microsoft Graph API")
            if graph_api.authenticate():
                # Update the shared Excel sheet with scraped data
                logger.log_info("Updating Excel sheet with scraped data")
                if graph_api.update_excel(tournament_data):
                    logger.log_info("Excel sheet updated successfully")
                else:
                    logger.log_error("Failed to update Excel sheet")
            else:
                logger.log_error("Failed to authenticate with Microsoft Graph API")

    except Exception as e:
        logger.log_error(f"An error occurred: {e}")

    finally:
        # Close the Selenium driver
        if 'scraper' in locals() and scraper:
            scraper.close_driver()
            logger.log_info("Selenium driver closed")
        
        logger.log_info("Script execution completed")

if __name__ == "__main__":
    main()