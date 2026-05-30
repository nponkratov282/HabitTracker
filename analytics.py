import questionary
import datetime
from habit import Habit


def show_current_habits(user_id: int):

    """Function to display the currently active habits"""

    questionary.print("\n--- Currently Tracked Habits ---",
                      style="bold underline")
    habits = Habit.get_by_user(user_id, active_only=True)
    if not habits:
        questionary.print("No active habits found.",
                          style="fg:yellow")
        return
    today = datetime.date.today()
    for habit in habits:
        current_s = habit.calculate_current_streak()
        longest_s = habit.calculate_longest_ever_streak()
        days_left = (habit.end_date - today).days

        questionary.print(
            f" {habit.name} ({habit.periodicity})\n"
            f" Current Streak: {current_s} | Longest Streak: {longest_s} | Ends in: {days_left} days")
    print("-" * 20)


def show_habits_by_periodicity(user_id: int):

    """Function to display the currently active habits sorted by periodicity"""

    period = questionary.select("Choose periodicity:", choices=['daily', 'weekly']).ask()
    if not period:
        return
    questionary.print(f"\n--- All '{period}' Habits (Active and Inactive) ---",
                      style="bold underline")
    all_habits = Habit.get_by_user(user_id, active_only=False)
    period_habits = [h for h in all_habits if h.periodicity == period]

    if not period_habits:
        questionary.print(f"No '{period}' habits found.",
                          style="fg:yellow")
        return
    
    for habit in period_habits:
        longest_s = habit.calculate_longest_ever_streak()
        status = "Active" if habit.end_date >= datetime.date.today() else "Expired"
        questionary.print(
            f"{habit.name} [{status}]\n"
            f"Longest Ever Streak: {longest_s}")
    print("-" * 20)


def show_longest_streak_period(user_id: int):

    """Function to display the longest streak for active habits by periodicity"""

    period = questionary.select("Choose periodicity:", choices=['daily', 'weekly']).ask()
    if not period:
        return
    all_habits = Habit.get_by_user(user_id, active_only=False)
    period_habits = [h for h in all_habits if h.periodicity == period]

    max_streak = 0
    best_habit_name = "n/a"

    if not period_habits:
        questionary.print(f"No '{period}' habits found to analyze.",
                          style="fg:yellow")
        return
    
    for habit in period_habits:
        streak = habit.calculate_longest_ever_streak()
        if streak > max_streak:
            max_streak = streak
            best_habit_name = habit.name

    questionary.print(f"\nLongest streak for '{period}' habits: {max_streak}",
                      style="bold")
    
    if max_streak > 0:
        questionary.print(f"(Achieved by: '{best_habit_name}')")
    print("-" * 20)


def show_longest_streak_all(user_id: int):

    """Function to display the longest streak among all active habits"""

    habits = Habit.get_by_user(user_id, active_only=False)

    max_streak = 0
    best_habit_name = "n/a"

    if not habits:
        questionary.print("No habits found to analyze.",
                          style="fg:yellow")
        return
    
    for habit in habits:
        streak = habit.calculate_longest_ever_streak()
        if streak > max_streak:
            max_streak = streak
            best_habit_name = habit.name
    
    questionary.print(f"\nLongest streak of all habits: {max_streak}",
                      style="bold")
    
    if max_streak > 0:
        questionary.print(f"(Achieved by: '{best_habit_name}')")
    print("-" * 20)