import unittest
import datetime
import os
import sqlite3

import db
from user import Users 
from habit import Habit
import analytics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
"""Checks that the database file location matches the test file location"""

class TestHabitTracker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        """Sets up a dedicated isolated database file for testing"""

        db.db_name = os.path.join(BASE_DIR, "test_habit_tracker.db")
        

    def setUp(self):

        """Initializes a clean database before running each individual test"""

        db.init_db()
        self.test_user_id = 1
        
        with db.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM completions")
            cur.execute("DELETE FROM habits")
            cur.execute("DELETE FROM users")
            conn.commit()

        self.setup_four_weeks_data()


    def tearDown(self):

        """Cleans up and removes the test database file after each test executed"""

        if os.path.exists(db.db_name):
            try:
                os.remove(db.db_name)
            except PermissionError:
                pass


    def setup_four_weeks_data(self):

        """Injects 28 consecutive days of completions for a daily habits,
        and 4 consecutive weeks of completions for a weekly habits"""

        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=30)).isoformat()
        end_date = (today + datetime.timedelta(days=60)).isoformat()

        
        with db.get_db_connection() as conn:

            """Directly injects test daily/monthly habits into the database"""

            cur = conn.cursor()
            
            cur.execute("""INSERT OR IGNORE INTO users (id, username, password_hash) 
                           VALUES (?, 'test_user', 'fake_hash')""", 
                        (self.test_user_id,))

            cur.execute("""INSERT INTO habits (id, user_id, name, description, periodicity, 
                        start_date, end_date) 
                           VALUES (101, ?, 'Test Daily', 'Desc', 'daily', ?, ?)""", 
                        (self.test_user_id, start_date, end_date))
            
            cur.execute("""INSERT INTO habits (id, user_id, name, description, periodicity, 
                        start_date, end_date) 
                           VALUES (102, ?, 'Test Weekly', 'Desc', 'weekly', ?, ?)""", 
                        (self.test_user_id, start_date, end_date))
            
            
            daily_completions = []
            for i in range(1, 29):
                completion_date = today - datetime.timedelta(days=i)
                daily_completions.append((101, completion_date.isoformat()))
                
            
            weekly_completions = []
            for w in range(1, 5):
                completion_date = today - datetime.timedelta(weeks=w)
                weekly_completions.append((102, completion_date.isoformat()))

            
            cur.executemany("INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)", 
                            daily_completions)
            cur.executemany("INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)", 
                            weekly_completions)
            conn.commit()

   
    def test_habit_creation(self):

        """Verify that a new habit can be successfully stored in the database"""

        today = datetime.date.today().isoformat()
        future_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        
        Habit.create(self.test_user_id, "Read Books", "Read 10 pages", "daily", future_date)
        
        user_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        habit_names = [h.name for h in user_habits]
        self.assertIn("Read Books", habit_names)


    def test_habit_editing(self):

        """Verify that modifications to an instantiated habit object persist correctly."""

        user_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        target_habit = [h for h in user_habits if h.id == 101][0]
        
        
        target_habit.name = "Updated Daily Name"
        target_habit.save()
        
        
        updated_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        updated_names = [h.name for h in updated_habits]
        self.assertIn("Updated Daily Name", updated_names)


    def test_habit_deletion(self):

        """Verify that removing a habit drops it completely from the user scope."""

        user_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        target_habit = [h for h in user_habits if h.id == 101][0]
        
        target_habit.delete()
        
        post_delete_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        habit_ids = [h.id for h in post_delete_habits]
        self.assertNotIn(101, habit_ids)

    
    def test_daily_streak_calculation(self):
        
        """Verify that daily habit processing reads 28 consecutive days as a streak of 28"""

        user_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        daily_habit = [h for h in user_habits if h.id == 101][0]
        
        longest_streak = daily_habit.calculate_longest_ever_streak()
        self.assertEqual(longest_streak, 28)


    def test_weekly_streak_calculation(self):

        """Verify that weekly habit processing reads 4 consecutive weeks as a streak of 4"""

        user_habits = Habit.get_by_user(self.test_user_id, active_only=False)
        weekly_habit = [h for h in user_habits if h.id == 102][0]
        
        longest_streak = weekly_habit.calculate_longest_ever_streak()
        self.assertEqual(longest_streak, 4)

if __name__ == "__main__":
    unittest.main()