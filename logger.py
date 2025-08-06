import logging as _logging
import os
from datetime import datetime

# Create logs directory next to this file
dir_path = os.path.dirname(__file__)
logs_dir = os.path.join(dir_path, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Log file with timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file = os.path.join(logs_dir, f'log_{timestamp}.log')

# Configure logger
logger = _logging.getLogger('arknights')
logger.setLevel(_logging.DEBUG)

# File handler
file_handler = _logging.FileHandler(log_file)
file_handler.setLevel(_logging.DEBUG)

# Console handler
console_handler = _logging.StreamHandler()
console_handler.setLevel(_logging.INFO)

# Formatter
tformatter = _logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(tformatter)
console_handler.setFormatter(tformatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
