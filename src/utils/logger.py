import logging
import os
import sys
from datetime import datetime

class Logger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
    def setup_logger(self):
        """Set up the logger with console and file handlers"""
        try:
            # Create logs directory if it doesn't exist
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
                
            # Set up logger configuration
            self.logger.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Set up console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            # Set up file handler
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.log_dir, f"scraper_{timestamp}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            # Add handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            
            self.logger.info("Logger initialized successfully")
            self.logger.info(f"Log file: {log_file}")
            return True
            
        except Exception as e:
            print(f"Error setting up logger: {e}")
            return False
        
    def log_info(self, message):
        """Log an info message"""
        self.logger.info(message)
        
    def log_error(self, message):
        """Log an error message"""
        self.logger.error(message)
        
    def log_warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
        
    def log_debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)