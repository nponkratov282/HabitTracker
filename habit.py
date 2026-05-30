import sqlite3
import datetime
from typing import List
from typing import Set
from db import get_db_connection


class Habit:

    """Defines the class for habits and corresponding defined functions"""

    def __init__(self, id: int, user_id: int, name: str, description: str,
                 periodicity: str, start_date: str, end_date: str):
        
        """Defines the Habit class' parameters"""

        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.start_date = datetime.date.fromisoformat(start_date)
        self.end_date = datetime.date.fromisoformat(end_date)

    
    def get_unique_periods(self) -> Set[datetime.date]:

        """Function to select sorted mark-done habits by periodicity"""

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""SELECT completion_date FROM completions
                                WHERE habit_id = ? ORDER BY completion_date ASC""",
                    (self.id,)
                )
                completions = [datetime.date.fromisoformat(row[0])
                               for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching completions for habit {self.id}: {e}")
            return set()
        
        unique_periods = set()
        if self.periodicity == 'daily':
            unique_periods = set(completions)
        else:
            for comp_date in completions:
                start_of_week = comp_date - datetime.timedelta(days=comp_date.weekday())
                unique_periods.add(start_of_week)
        
        return unique_periods
    

    def calculate_current_streak(self) -> int:

        """Function to calculate the current streak for chosen habit"""

        sorted_periods = sorted(list(self.get_unique_periods()),
                                reverse=True)
        if not sorted_periods:
            return 0
        
        today = datetime.date.today()
        current_streak = 0

        if self.periodicity == 'daily':
            delta = datetime.timedelta(days=1)
            reference_date = today
            if reference_date not in sorted_periods:
                reference_date = today - delta

        else:
            delta = datetime.timedelta(weeks=1)
            reference_date = today - datetime.timedelta(days=today.weekday())
            if reference_date not in sorted_periods:
                reference_date = reference_date - delta

        if reference_date not in sorted_periods:
            return 0
        
        current_streak = 0
        for period_start in sorted_periods:
            if period_start == reference_date:
                current_streak += 1
                reference_date -= delta
            elif period_start < reference_date:
                break

        return current_streak
    

    def calculate_longest_ever_streak(self) -> int:

        """Function to calculate the longest streak ever among all"""

        sorted_periods = sorted(list(self.get_unique_periods()))
        if not sorted_periods:
            return 0
        
        max_streak = 0
        current_streak = 0
        last_period = None

        delta = datetime.timedelta(days=1) if self.periodicity == 'daily' else datetime.timedelta(weeks=1)

        for period in sorted_periods:
            if last_period is None:
                current_streak = 1
            elif period == last_period + delta:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
            last_period = period
        
        return max(max_streak, current_streak)
    

    def mark_done(self) -> bool:

        """Function to mark the habit completed"""

        today = datetime.date.today()
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                cur.execute("""SELECT MAX(completion_date) FROM completions 
                                WHERE habit_id = ?""",
                    (self.id,)
                )
                last_completion_str = cur.fetchone()[0]

                if last_completion_str:
                    last_completion_date = datetime.date.fromisoformat(last_completion_str)
                    if self.periodicity == 'daily' and last_completion_date == today:
                        return False
                    elif self.periodicity == 'weekly':
                        start_of_this_week = today - datetime.timedelta(days=today.weekday())
                        if last_completion_date >= start_of_this_week:
                            return False
                
                cur.execute(
                    "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
                    (self.id, today.isoformat())
                )
                conn.commit()
                return True
            
        except sqlite3.Error as e:
            print(f"An error occured while making habit done: {e}")
            return False
    

    def save(self):

        """Function to save and update the habit values in the database"""

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE habits
                    SET name = ?, description = ?, periodicity = ?, end_date = ? 
                    WHERE id = ?""",
                    (self.name, self.description, self.periodicity, 
                     self.end_date.isoformat(), self.id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occured while updating the habit: {e}")


    def delete(self):

        """Function to remove the habit entry from the database"""

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM habits WHERE id = ?",
                    (self.id,)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occured while deleting the habit: {e}")

    @staticmethod
    def create(user_id: int, name: str, description: str,
               periodicity: str, end_date: str):
        start_date = datetime.date.today().isoformat()
        """Function to create the habit entry in the database as per users choice"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO habits(
                            user_id, name, description, periodicity, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, name, description, periodicity, start_date, end_date)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occured while creating the habit: {e}")
    

    @staticmethod
    def get_by_user(user_id: int, active_only: bool = False) -> List['Habit']:

        """Function to agregate the habits associated with the user"""
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                query = "SELECT * FROM habits WHERE user_id = ?"
                params = [user_id]

                if active_only:
                    today = datetime.date.today().isoformat()
                    query += " AND end_date >= ?"
                    params.append(today)
                
                cur.execute(query, tuple(params))
                rows = cur.fetchall()

                return [Habit(*row) for row in rows]
        except sqlite3.Error as e:
            print(f"An error occured fetching habits: {e}")
            return []
        