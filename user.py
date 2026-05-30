import hashlib
import sqlite3
import questionary
from typing import Optional
from db import get_db_connection
from predefined import add_predefined_habits


class Users:

    """Defines the class for users and corresponding defined functions"""

    @staticmethod 
    def hash_password(password: str) -> str:

        """Function to hash the user's password in sha256 format for security"""

        return hashlib.sha256(password.encode()).hexdigest()
    

    @staticmethod 
    def check_password(stored_hash: str, provided_password: str) -> bool:

        """Function to check the entered password against stored hashed version of password"""

        return stored_hash == Users.hash_password(provided_password)
    

    @staticmethod 
    def register_user():

        """Function that creates the user profile with entered password and username,
        provides user with choice to generate predefined habits"""

        username = questionary.text("Enter username:").ask()
        password = questionary.password("Enter password:").ask()
        if not username or not password:
            questionary.print("These fields cannot be empty.",
                              style="fg:red")
            return None
        
        password_hash = Users.hash_password(password)

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO users(
                            username, 
                            password_hash) 
                            VALUES (?, ?)""",
                            (username, 
                             password_hash))
                
                new_user_id = cur.lastrowid

                add_predefined = questionary.confirm(
                    "Do you want 5 predefined habits to get familiar with the structure?"
                    ).ask()
                
                if add_predefined:
                    add_predefined_habits(new_user_id, conn)
                conn.commit()
                questionary.print(f"User '{username}' registration complete!",
                                  style="fg:green")
                
        except sqlite3.IntegrityError:
            questionary.print(f"Username: '{username}' already exists.",
                              style="fg:red")
            
        except sqlite3.Error as e:
            questionary.print(f"An error occured: {e}",
                              style="fg:red")
            raise e
    

    @staticmethod 
    def login() -> Optional[int]:

        """Function for user authorization process with input of username and password"""

        username = questionary.text("Username:").ask()
        password = questionary.password("Password:").ask()

        if not username or not password:
            questionary.print("Please enter correct credentials.",
                              style="fg:red")
            return None
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, password_hash FROM users WHERE username = ?",
                    (username,))

                user_data = cur.fetchone()

            if user_data:
                user_id, stored_hash = user_data
                if Users.check_password(stored_hash, password):
                    questionary.print(f"Welcome back, {username}!",
                                      style="fg:green")
                    return user_id
                else:
                    questionary.print("Incorrect password.",
                                      style="fg:red")
           
            else:
                questionary.print("This user does not exist.",
                                  style="fg:red")
            return None
        
        except sqlite3.Error as e:
            questionary.print(f"An error occured: {e}",
                              style="fg:red")
            return None