import logging
import os

def get_logger(name: str = "framework") -> logging.Logger:
    """Returns a configured logger instance that writes to logs/framework.log and console."""
    logger = logging.getLogger(name)
    
    # If logger is already configured, return it
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File Handler
    file_handler = logging.FileHandler("logs/framework.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid double logging in pytest
    logger.propagate = False
    
    return logger

# Global default logger instance
logger = get_logger()
