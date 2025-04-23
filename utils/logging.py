import logging

# Basic logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger that can be imported
logger = logging.getLogger('my_app')