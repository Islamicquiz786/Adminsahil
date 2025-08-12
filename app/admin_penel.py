import logging
from telegram_bot.bot import setup_bot
from config.telegram_config import TELEGRAM_ADMIN_ID

class AdminPanel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bot = setup_bot()
        self.admin_id = TELEGRAM_ADMIN_ID

    def send_admin_notification(self, message):
        """Send notification to admin via Telegram"""
        try:
            self.bot.bot.send_message(chat_id=self.admin_id, text=message)
            self.logger.info(f"Notification sent to admin: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")

    def monitor_activity(self, activity):
        """Monitor and log activities"""
        log_message = f"Activity detected: {activity}"
        self.logger.info(log_message)
        self.send_admin_notification(log_message)