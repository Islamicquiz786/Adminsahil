import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from config.telegram_config import TelegramConfig  # Updated import

# 1. Enhanced Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 2. New Command Handlers
def start(update: Update, context: CallbackContext):
    """Enhanced start command with user tracking"""
    user = update.effective_user
    logger.info(f"New user started bot: {user.id} - {user.name}")
    
    update.message.reply_text(
        f'✅ Admin Panel Bot Active\n'
        f'User ID: {user.id}\n'
        f'Name: {user.full_name}'
    )
    
    # Notify admin
    context.bot.send_message(
        chat_id=TelegramConfig.ADMIN_ID,
        text=f"🆕 New user started bot:\n"
             f"ID: {user.id}\n"
             f"Name: {user.name}"
    )

def error_handler(update: Update, context: CallbackContext):
    """Enhanced error handling"""
    logger.error(f'Error: {context.error}', exc_info=True)
    if update:
        context.bot.send_message(
            chat_id=TelegramConfig.ADMIN_ID,
            text=f"❌ Bot Error:\n{context.error}"
        )

# 3. Improved Bot Setup
def setup_bot():
    """Enhanced bot initialization"""
    try:
        updater = Updater(
            token=TelegramConfig.BOT_TOKEN,
            use_context=True,
            request_kwargs={
                'read_timeout': TelegramConfig.REQUEST_TIMEOUT,
                'connect_timeout': TelegramConfig.REQUEST_TIMEOUT
            }
        )
        
        dp = updater.dispatcher
        
        # Command Handlers
        dp.add_handler(CommandHandler("start", start))
        
        # Error Handler
        dp.add_error_handler(error_handler)
        
        # Startup Notification
        updater.bot.send_message(
            chat_id=TelegramConfig.ADMIN_ID,
            text="🤖 Bot started successfully!\n"
                 f"Polling timeout: {TelegramConfig.POLLING_TIMEOUT}s"
        )
        
        updater.start_polling(
            poll_interval=TelegramConfig.POLLING_INTERVAL,
            timeout=TelegramConfig.POLLING_TIMEOUT
        )
        logger.info("Bot started with enhanced configuration")
        return updater
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    TelegramConfig.validate()  # Verify config first
    bot_instance = setup_bot()
    bot_instance.idle()
