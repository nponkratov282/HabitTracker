import sys
import questionary
import datetime
from typing import Optional

from db import init_db
from user import Users
from habit import Habit
from utils import check_date_validity, check_date_in_future
import analytics

def ui_select_habit(user_id: int, message: str, active_only: bool = False):

    """Function for selection menu to display available habits for user"""

    habits = Habit.get_by_user(user_id, active_only=active_only)
    if not habits:
        questionary.print("You have no habits to show.",
                          style="fg:yellow")
        return None
    
    habit_choices = [questionary.Choice(
            title=f"{h.name} ({h.periodicity}) - Ends: {h.end_date.isoformat()}",
            value=h)
        for h in habits]
    
    selected_habit = questionary.select(message, choices=habit_choices).ask()
    return selected_habit


def ui_add_habit(user_id: int):

    """Function for menu option to create the habit"""
    
    name = questionary.text("Habit name:").ask()
    if not name:
        questionary.print("Habit name is incorrect.",
                          style="fg:red")
        return
    
    description = questionary.text("Description (optional):").ask()
    periodicity = questionary.select("periodicity:", choices=["daily", "weekly"]).ask()
    end_date = questionary.text("End date (yy-mm-dd):",
                                validate=lambda 
                                text: check_date_validity(text) and check_date_in_future(text)).ask()
    
    Habit.create(user_id, name, description, periodicity, end_date)
    questionary.print(f"Habit '{name}' created successfully!",
                      style="fg:green")


def ui_edit_habit(user_id: int):

    """Function for 'edit' submenu to amend the habits available for user"""

    habits = ui_select_habit(user_id, "Which habit do you wish to edit?")
    if not habits:
        return
    
    new_name = questionary.text("New name:",
                                default=habits.name).ask()
    if not new_name:
        questionary.print("Habit name cannot be empty",
                          style="fg:red")
        return
    
    new_desc = questionary.text("New description:",
                                default=habits.description).ask()
    new_period = questionary.select("New periodicity:", choices=["daily", "weekly"],
                                    default=habits.periodicity).ask()
    new_end_date = questionary.text("New end date (yyyy-mm-dd):",
                                    default=habits.end_date.isoformat(),
                                    validate=lambda
                                    text: check_date_validity(text) and check_date_in_future(text)).ask()
    
    habits.name = new_name
    habits.description = new_desc
    habits.periodicity = new_period
    habits.end_date = datetime.date.fromisoformat(new_end_date)

    habits.save()
    questionary.print(f"Habit '{habits.name}' updated successfully.",
                      style="fg:green")
    

def ui_delete_habit(user_id: int):

    """Function to create delete submenu to remove the habit entry by user"""

    habit = ui_select_habit(user_id, "Which habit do you want to delete?")
    if not habit:
        return
    
    confirm = questionary.confirm(
        f"Are you sure you want to delete '{habit.name}'? \nThis will result in losing associated progress data.").ask()
    
    if confirm:
        habit.delete()
        questionary.print(f"Habit '{habit.name}' deleted successfully.",
                          style="fg:green")


def ui_mark_habit_done(user_id: int):

    """Function for 'mark done' submenu option to mark habit done for today"""

    habit = ui_select_habit(user_id, "Which habit was completed?",
                            active_only=True)
    if not habit:
        return
    success = habit.mark_done()

    if success:
        questionary.print(f"Well done, '{habit.name}' is marked as done.",
                          style="fg:green")
        current_s = habit.calculate_current_streak()
        questionary.print(f"Your current streak for '{habit.name}' is: {current_s}",
                          style="fg:cyan")
    else:
        questionary.print(
            f"'{habit.name}' is already marked done for this {habit.periodicity}.",
            style="fg:yellow")
        

def analytics_menu(user_id: int):

    """Function that creates the analytics submenu with access to habit analytics
    - active habits, active habits sorted by periodicity, longest streak ever, and
    longest streak by periodicity"""

    while True:
        choice = questionary.select("Analytics menu:",
                                    choices=[
                                        "1. List of active tracked habits",
                                        "2. List of habits by periodicity",
                                        "3. Longest streak (by periodicity)",
                                        "4. Longest streak (ever)",
                                        "Back to main menu"]
                                        ).ask()
        
        if not choice or choice == "Back to main menu":
            break
        
        elif choice == "1. List of active tracked habits":
            analytics.show_current_habits(user_id)
        elif choice == "2. List of habits by periodicity":
            analytics.show_habits_by_periodicity(user_id)
        elif choice == "3. Longest streak (by periodicity)":
            analytics.show_longest_streak_period(user_id)
        elif choice == "4. Longest streak (ever)":
            analytics.show_longest_streak_all(user_id)

        questionary.press_any_key_to_continue().ask()


def main_menu(user_id: int):

    """Function that creates the action tree for the main menu with following submenus:
    mark done, add new, edit, delete, view analytics, logout"""

    while True:
        choice = questionary.select("Main menu:",
                                    choices=[
                                        "Mark done",
                                        "Add new",
                                        "Edit",
                                        "Delete",
                                        "View analytics",
                                        "Logout"]
                                    ).ask()
        
        if not choice or choice == "Logout":
            questionary.print("Logging out. See you soon!",
                              style="fg:cyan")
            break
       
        elif choice == "Mark done":
            ui_mark_habit_done(user_id)
        elif choice ==  "Add new":
            ui_add_habit(user_id)
        elif choice == "Edit":
            ui_edit_habit(user_id)
        elif choice == "Delete":
            ui_delete_habit(user_id)
        elif choice == "View analytics":
            analytics_menu(user_id)

        questionary.press_any_key_to_continue().ask()


def main():

    """Function that initiates the programm - habit tracker
    Upon initiation programm offers user to register or logout (if alreafy registered)"""

    print("Initializing habit tracker ///")
    init_db()

    while True:
        choice = questionary.select("Habit tracker is ready",
                                    choices=[
                                    "Login",
                                    "Register",
                                    "Exit"]
                                    ).ask()
        
        if not choice or choice == "Exit":
            print("Exiting the program. \nCome back later")
            sys.exit(0)
        
        elif choice == "Login":
            user_id = Users.login()
            if user_id:
                main_menu(user_id)
        elif choice == "Register":
            Users.register_user()

if __name__ == "__main__":
    main()