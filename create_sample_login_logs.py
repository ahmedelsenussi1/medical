from app import app, db
from models import User, LoginLog
from datetime import datetime, timedelta
import random
import ipaddress

# Common user agents for variety
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

def generate_ip():
    """Generate a random IP address"""
    return str(ipaddress.IPv4Address(random.randint(0, 2**32-1)))

def create_login_logout_pair(user, date, ip=None):
    """Create a login and logout pair for a user on a specific date"""
    if ip is None:
        ip = generate_ip()
    
    user_agent = random.choice(user_agents)
    
    # Random login time between 8 AM and 5 PM
    login_hour = random.randint(8, 16)
    login_minute = random.randint(0, 59)
    login_time = date.replace(hour=login_hour, minute=login_minute)
    
    # Session duration between 30 minutes and 8 hours (in minutes)
    session_duration = random.randint(30, 480)
    logout_time = login_time + timedelta(minutes=session_duration)
    
    # Create login record
    login_log = LoginLog(
        user_id=user.id,
        action='login',
        timestamp=login_time,
        ip_address=ip,
        user_agent=user_agent
    )
    
    # Create logout record
    logout_log = LoginLog(
        user_id=user.id,
        action='logout',
        timestamp=logout_time,
        ip_address=ip,
        user_agent=user_agent,
        session_duration=session_duration
    )
    
    return login_log, logout_log

with app.app_context():
    # Clear existing logs if needed
    # Uncomment the next line if you want to delete all existing logs
    # LoginLog.query.delete()
    
    # Get all users
    users = User.query.all()
    
    if not users:
        print("No users found in the database. Please create users first.")
        exit()
    
    print(f"Found {len(users)} users in the database")
    
    # Generate logs for the past 30 days
    today = datetime.now()
    logs_to_add = []
    
    for day in range(30):
        date = today - timedelta(days=day)
        
        # Each user logs in 0-3 times per day
        for user in users:
            login_count = random.randint(0, 3)
            
            for _ in range(login_count):
                login, logout = create_login_logout_pair(user, date)
                logs_to_add.append(login)
                logs_to_add.append(logout)
    
    # Add all logs to the database
    db.session.add_all(logs_to_add)
    db.session.commit()
    
    print(f"Added {len(logs_to_add)} login/logout records to the database")
    print(f"Total login logs: {LoginLog.query.filter_by(action='login').count()}")
    print(f"Total logout logs: {LoginLog.query.filter_by(action='logout').count()}")