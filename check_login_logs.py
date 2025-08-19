from app import app, db
from models import User, LoginLog
import random
from datetime import datetime, timedelta

# This script checks and adds sample login logs for all users

with app.app_context():
    # Get all users
    users = User.query.all()
    
    print(f"Found {len(users)} users in the database")
    
    # Check existing login logs
    logs = LoginLog.query.all()
    print(f"Found {len(logs)} login logs in the database")
    
    # Group logs by user
    user_logs = {}
    for log in logs:
        if log.user_id not in user_logs:
            user_logs[log.user_id] = []
        user_logs[log.user_id].append(log)
    
    # Print logs per user
    for user in users:
        user_log_count = len(user_logs.get(user.id, []))
        print(f"User {user.username} (ID: {user.id}) has {user_log_count} login logs")
    
    # Add sample login logs for users with no logs
    add_sample_logs = input("Do you want to add sample login logs for users with no logs? (y/n): ")
    
    if add_sample_logs.lower() == 'y':
        now = datetime.now()
        sample_ips = ['127.0.0.1', '192.168.1.1', '10.0.0.1']
        sample_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        for user in users:
            # Skip if user already has logs
            if user.id in user_logs and len(user_logs[user.id]) > 0:
                continue
            
            print(f"Adding sample logs for user {user.username}")
            
            # Add 5 pairs of login/logout logs over the past 5 days
            for i in range(5):
                login_time = now - timedelta(days=i, hours=random.randint(0, 12))
                logout_time = login_time + timedelta(minutes=random.randint(30, 480))  # 30 min to 8 hours session
                
                ip = random.choice(sample_ips)
                agent = random.choice(sample_agents)
                
                # Create login log
                login_log = LoginLog(
                    user_id=user.id,
                    action='login',
                    timestamp=login_time,
                    ip_address=ip,
                    user_agent=agent
                )
                
                # Create logout log
                logout_log = LoginLog(
                    user_id=user.id,
                    action='logout',
                    timestamp=logout_time,
                    ip_address=ip,
                    user_agent=agent
                )
                
                db.session.add(login_log)
                db.session.add(logout_log)
            
        db.session.commit()
        print("Sample login logs added successfully!")