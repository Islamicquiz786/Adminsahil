from config.telegram_config import TelegramConfig

class AdminConsole:
    @staticmethod
    def system_status():
        """Get current system status"""
        return {
            'bot_active': True,
            'last_activity': '2023-08-25 14:30',
            'users_connected': 5
        }

    @classmethod
    def generate_report(cls):
        """Generate admin report"""
        status = cls.system_status()
        return (
            f"📊 Admin Report\n"
            f"Bot Token: {TelegramConfig.BOT_TOKEN[:5]}...\n"
            f"Last Active: {status['last_activity']}\n"
            f"Connected Users: {status['users_connected']}"
        )
