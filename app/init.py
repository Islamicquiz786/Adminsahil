# AdminPanel/app/__init__.py
"""
Admin Panel Package Initialization

This file makes the 'app' directory a Python package and handles:
- Core component initialization
- Database setup
- Logger configuration
- Global imports
"""

import logging
from .database import db  # Database instance
from .utilities import timestamp, rate_limited
from .notifications import send_alert, send_status
from .monitor import SystemMonitor
from .admin_console import AdminConsole

# Initialize package-level logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('admin_panel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Package version
__version__ = '1.0.0'

# Package exports
__all__ = [
    'db',
    'timestamp',
    'rate_limited',
    'send_alert',
    'send_status',
    'SystemMonitor',
    'AdminConsole',
    'logger'
]

# Initialize components on import
logger.info(f"Initializing Admin Panel v{__version__}")
db.log_activity(0, 'system', 'Package initialized')

# Example usage when imported:
if __name__ == '__main__':
    print(f"Admin Panel Package v{__version__}")
    print("Available components:", __all__)