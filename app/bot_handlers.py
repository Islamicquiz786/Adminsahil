# AdminPanel/app/bot_handlers.py
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler
from config.telegram_config import TelegramConfig
from app.database import db
from app.notifications import send_alert
from app.utilities import timestamp, rate_limited
import logging

logger = logging.getLogger(__name__)

# Decorator to restrict commands to admin only
def admin_only(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if str(user_id) != TelegramConfig.ADMIN_ID:
            update.message.reply_text("⛔ Unauthorized: Admin access required")
            logger.warning(f"Unauthorized access attempt by {user_id}")
            return
        return func(update, context)
    return wrapper

# Core Commands
@rate_limited(5, 60)  # 5 calls per minute
def start(update: Update, context: CallbackContext):
    """Welcome message and user registration"""
    user = update.effective_user
    db.add_user({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
    
    welcome_msg = (
        f"👋 Welcome *{user.first_name}*!\n"
        f"🆔 Your ID: `{user.id}`\n"
        f"🕒 {timestamp()}"
    )
    
    update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Log activity
    db.log_activity(user.id, 'command', '/start')
    logger.info(f"New start command from {user.id}")

@admin_only
def status(update: Update, context: CallbackContext):
    """System status overview (Admin only)"""
    from app.monitor import SystemMonitor
    from app.admin_console import AdminConsole
    
    resources = SystemMonitor.check_resources()
    report = AdminConsole.generate_report()
    
    status_msg = (
        "📊 *System Status*\n"
        "━━━━━━━━━━━━━━\n"
        f"{report}\n\n"
        "🖥️ *Resources*\n"
        "━━━━━━━━━━━━━━\n"
        f"• CPU: {resources['cpu']}%\n"
        f"• Memory: {resources['memory']}%\n"
        f"• Disk: {resources['disk']}%"
    )
    
    update.message.reply_text(
        status_msg,
        parse_mode=ParseMode.MARKDOWN
    )
    db.log_activity(update.effective_user.id, 'command', '/status')

# Admin Commands
@admin_only
def alerts(update: Update, context: CallbackContext):
    """Show unresolved alerts (Admin only)"""
    alerts = db.get_unresolved_alerts()
    
    if not alerts:
        update.message.reply_text("✅ No active alerts")
        return
    
    alert_list = "\n".join(
        f"⚠️ {alert['alert_type'].upper()}: {alert['message']}"
        f" (ID: {alert['alert_id']})"
        for alert in alerts
    )
    
    update.message.reply_text(
        f"🚨 *Active Alerts*\n━━━━━━━━━━━━━━\n{alert_list}",
        parse_mode=ParseMode.MARKDOWN
    )
    db.log_activity(update.effective_user.id, 'command', '/alerts')

@admin_only
def log(update: Update, context: CallbackContext):
    """Show recent activities (Admin only)"""
    activities = db.get_recent_activities(5)
    
    activity_list = "\n".join(
        f"{a['timestamp']} - {a['activity_type']}: {a['details'] or ''}"
        for a in activities
    )
    
    update.message.reply_text(
        f"📝 *Recent Activities*\n━━━━━━━━━━━━━━\n{activity_list}",
        parse_mode=ParseMode.MARKDOWN
    )
    db.log_activity(update.effective_user.id, 'command', '/log')

# Command Handlers Setup
def setup_handlers(dispatcher):
    """Register all command handlers"""
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("alerts", alerts))
    dispatcher.add_handler(CommandHandler("log", log))
    
    logger.info("Bot command handlers registered")

# Example usage when testing
if __name__ == '__main__':
    from telegram.ext import Updater
    logging.basicConfig(level=logging.INFO)
    
    updater = Updater(token=TelegramConfig.BOT_TOKEN, use_context=True)
    setup_handlers(updater.dispatcher)
    
    print("Test handlers registered. Use /start, /status, etc.")
    updater.start_polling()
    updater.idle()