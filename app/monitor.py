import psutil
from config.telegram_config import TelegramConfig

class SystemMonitor:
    @staticmethod
    def check_resources():
        """Monitor system resources"""
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }

    @classmethod
    def resource_alert(cls):
        """Generate resource alerts"""
        resources = cls.check_resources()
        if resources['memory'] > 80:
            return f"⚠️ High Memory Usage: {resources['memory']}%"
        return None