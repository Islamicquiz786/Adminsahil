from admin_panel import AdminPanel
import time
import random

def simulate_activity(admin_panel):
    """Simulate various activities for testing"""
    activities = [
        "User login attempt",
        "File upload detected",
        "Database query executed",
        "Configuration change",
        "Security alert triggered"
    ]
    
    while True:
        activity = random.choice(activities)
        admin_panel.monitor_activity(activity)
        time.sleep(random.randint(5, 15))

if __name__ == "__main__":
    print("Starting Admin Panel with Telegram Integration")
    admin_panel = AdminPanel()
    try:
        simulate_activity(admin_panel)
    except KeyboardInterrupt:
        print("\nAdmin Panel stopped")