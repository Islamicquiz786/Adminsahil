from config.telegram_config import TelegramConfig
from telegram import Bot

bot = Bot(token=TelegramConfig.BOT_TOKEN)

def send_alert(message):
    """Send alert to admin"""
    bot.send_message(
        chat_id=TelegramConfig.ADMIN_ID,
        text=f"🚨 ALERT: {message}"
    )

def send_status(message):
    """Send status update"""
    bot.send_message(
        chat_id=TelegramConfig.ADMIN_ID,
        text=f"ℹ️ STATUS: {message}"
    )