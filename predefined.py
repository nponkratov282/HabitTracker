import sqlite3
from sqlite3 import *
import datetime

predefined_habits = [
    {"name": "Brush teeth",
     "description": "Brush teeth for 3 minutes",
     "periodicity": "daily"},
    {"name": "Water plants",
     "description": "Water plants before leaving the home",
     "periodicity": "daily"},
    {"name": "Yoga",
     "description": "Do daily set of exercises",
     "periodicity": "daily"},
    {"name": "Groceries",
     "description": "Buy groceries for the week",
     "periodicity": "weekly"},
    {"name": "Sunday mess",
     "description": "Attend the Sunday mess",
     "periodicity": "weekly"}
]


def add_predefined_habits(user_id: int, conn: sqlite3.Connection):

    """Function that inserts predefined habits into the habits database 
    upon user's choice during the sign up procedure"""

    try:
        cur = conn.cursor()
        today = datetime.date.today()
        end_date = (datetime.timedelta(days=90) + today).isoformat()
        start_date = today.isoformat()

        for habit in predefined_habits:
            cur.execute(""" INSERT INTO habits(
                         user_id, 
                         name, 
                         description, 
                         periodicity, 
                         start_date, 
                         end_date)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, 
                 habit["name"], 
                 habit["description"], 
                 habit["periodicity"],
                 start_date, 
                 end_date))
            
            print("5 predefined habits were added.")
    
    except sqlite3.Error as e:

        """Reverts with error msg if any occur during the habit database population
         with predefined data"""
        
        print(f"An error has occured: {e}")
        raise e