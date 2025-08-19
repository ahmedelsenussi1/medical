from app import app, db
from models import LoginLog, User
from datetime import datetime, timedelta
import random
import uuid
import user_agents

# This script ensures the login_logs table is created and populated with test data

def parse_user_agent(user_agent_string):
    """تحليل سلسلة وكيل المستخدم واستخراج معلومات الجهاز والمتصفح ونظام التشغيل"""
    try:
        user_agent = user_agents.parse(user_agent_string)
        return {
            'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
            'os': f"{user_agent.os.family} {user_agent.os.version_string}",
            'device_type': 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'Desktop'
        }
    except:
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device_type': 'Unknown'
        }

# إضافة دالة للتأكد من أن البيانات قابلة للتحويل إلى JSON
def ensure_json_serializable(obj):
    """التأكد من أن الكائن قابل للتحويل إلى JSON"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [ensure_json_serializable(item) for item in obj]
    # إذا كان الكائن من نوع آخر، حاول تحويله إلى سلسلة نصية
    try:
        return str(obj)
    except:
        return None

with app.app_context():
    # Create the login_logs table
    db.create_all()
    
    # Check if we have any login logs
    if LoginLog.query.count() == 0:
        print("إنشاء سجلات تسجيل دخول للمستخدمين...")
        
        # Get all users
        users = User.query.all()
        
        if users:
            # Sample user agents
            sample_user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
            ]
            
            # Sample IP addresses
            sample_ips = [
                '192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4',
                '10.0.0.1', '10.0.0.2', '10.0.0.3',
                '172.16.0.1', '172.16.0.2',
                '127.0.0.1'
            ]
            
            # Generate login logs for the past 30 days
            now = datetime.now()
            all_logs = []
            
            for user in users:
                # Generate between 10 and 50 login sessions for each user
                num_sessions = random.randint(10, 50)
                
                for i in range(num_sessions):
                    # Generate random login time within the past 30 days
                    days_ago = random.randint(0, 30)
                    hours = random.randint(8, 18)  # Business hours
                    minutes = random.randint(0, 59)
                    
                    login_time = now - timedelta(days=days_ago, hours=now.hour-hours, minutes=now.minute-minutes)
                    
                    # Session duration between 15 minutes and 8 hours
                    session_duration = random.randint(15, 480)
                    logout_time = login_time + timedelta(minutes=session_duration)
                    
                    # If logout time is in the future, set it to now
                    if logout_time > now:
                        logout_time = now
                        session_duration = int((logout_time - login_time).total_seconds() / 60)
                    
                    # Random user agent and IP
                    user_agent_string = random.choice(sample_user_agents)
                    ip_address = random.choice(sample_ips)
                    
                    # Parse user agent
                    ua_info = parse_user_agent(user_agent_string)
                    
                    # Generate session ID
                    session_id = str(uuid.uuid4())
                    
                    # Create login log
                    login_log = LoginLog(
                        user_id=user.id,
                        action='login',
                        timestamp=login_time,
                        ip_address=ip_address,
                        user_agent=user_agent_string,
                        session_id=session_id,
                        device_type=ua_info['device_type'],
                        browser=ua_info['browser'],
                        os=ua_info['os'],
                        status='success'
                    )
                    
                    # Create logout log
                    logout_log = LoginLog(
                        user_id=user.id,
                        action='logout',
                        timestamp=logout_time,
                        ip_address=ip_address,
                        user_agent=user_agent_string,
                        session_id=session_id,
                        device_type=ua_info['device_type'],
                        browser=ua_info['browser'],
                        os=ua_info['os'],
                        session_duration=session_duration,
                        status='success'
                    )
                    
                    all_logs.append(login_log)
                    all_logs.append(logout_log)
            
            # Add all logs to the database
            db.session.add_all(all_logs)
            db.session.commit()
            print(f"Added {len(all_logs)} sample login logs for {len(users)} users")
            
            # Add some failed login attempts for realism
            failed_logs = []
            for user in users:
                # Add 1-5 failed login attempts
                num_failed = random.randint(1, 5)
                for i in range(num_failed):
                    # Random time in the past 30 days
                    days_ago = random.randint(0, 30)
                    hours = random.randint(0, 23)
                    minutes = random.randint(0, 59)
                    
                    failed_time = now - timedelta(days=days_ago, hours=now.hour-hours, minutes=now.minute-minutes)
                    
                    # Random user agent and IP
                    user_agent_string = random.choice(sample_user_agents)
                    ip_address = random.choice(sample_ips)
                    
                    # Parse user agent
                    ua_info = parse_user_agent(user_agent_string)
                    
                    # Create failed login log
                    failed_log = LoginLog(
                        user_id=user.id,
                        action='login',
                        timestamp=failed_time,
                        ip_address=ip_address,
                        user_agent=user_agent_string,
                        device_type=ua_info['device_type'],
                        browser=ua_info['browser'],
                        os=ua_info['os'],
                        status='failed'
                    )
                    
                    failed_logs.append(failed_log)
            
            # Add failed login attempts to the database
            if failed_logs:
                db.session.add_all(failed_logs)
                db.session.commit()
                print(f"Added {len(failed_logs)} failed login attempts")
                
            # Calculate and update session durations for existing logs
            print("Calculating session durations for existing logs...")
            users = User.query.all()
            for user in users:
                # Get all login logs for this user
                login_logs = LoginLog.query.filter_by(user_id=user.id, action='login').order_by(LoginLog.timestamp).all()
                
                # Get all logout logs for this user
                logout_logs = LoginLog.query.filter_by(user_id=user.id, action='logout').order_by(LoginLog.timestamp).all()
                
                # Create a dictionary of session IDs to logout logs
                logout_dict = {log.session_id: log for log in logout_logs if log.session_id}
                
                # Update session durations
                for login in login_logs:
                    if login.session_id and login.session_id in logout_dict:
                        logout = logout_dict[login.session_id]
                        duration = int((logout.timestamp - login.timestamp).total_seconds() / 60)
                        if duration >= 0:
                            logout.session_duration = duration
            
            db.session.commit()
            print("Session durations updated successfully")
        else:
            print("No users found in the database")
    else:
        print(f"Login logs table already has {LoginLog.query.count()} records")
    
    print("Login logs table is ready!")