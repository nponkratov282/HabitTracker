import hashlib
import datetime
import db 

def seed_main_app_data():
    # Make sure we are targeting the real app database!
    db.init_db() 
    
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=30)).isoformat()
    end_date = (today + datetime.timedelta(days=60)).isoformat()

    with db.get_db_connection() as conn:
        cur = conn.cursor()
        
        test_password = "password123"
        valid_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        cur.execute("""INSERT OR IGNORE INTO users (id, username, password_hash) 
                       VALUES (999, 'test_user', ?)""", (valid_hash,))
        
        # 2. Inject a Daily and Weekly habit
        cur.execute("""INSERT INTO habits (id, user_id, name, description, periodicity, start_date, end_date) 
                       VALUES (998, 999, '28-Day Daily Streak', 'Testing Daily', 'daily', ?, ?)""", 
                    (start_date, end_date))
        
        cur.execute("""INSERT INTO habits (id, user_id, name, description, periodicity, start_date, end_date) 
                       VALUES (999, 999, '4-Week Weekly Streak', 'Testing Weekly', 'weekly', ?, ?)""", 
                    (start_date, end_date))
        
        # 3. Generate the 4 weeks of completions
        daily_completions = [(998, (today - datetime.timedelta(days=i)).isoformat()) for i in range(1, 29)]
        weekly_completions = [(999, (today - datetime.timedelta(weeks=w)).isoformat()) for w in range(1, 5)]

        cur.executemany("INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)", 
                        daily_completions)
        cur.executemany("INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)", 
                        weekly_completions)
        
        conn.commit()
        print("Ok. 4 weeks of records inserted into habit tracker database.")
        print("Username to login: test_user")
        print("Password to login: password123")

if __name__ == "__main__":
    seed_main_app_data()