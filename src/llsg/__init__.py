import logging

def setup_logger(log_file=None, log_level=logging.INFO):
    """
    Set up the logger for the application.
    """
    logger = logging.getLogger('llsg_stimulator')
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Initialize the logger
logger = setup_logger()