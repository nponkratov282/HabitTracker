# Habit Tracker Application
Tool for tracking and analyzing your habits daily/weekly utilizing CLI.

## INSTALLATION
1. Clone the repository.
2. Run 'python main.py' to start the application.
3. Run 'python test_habit_records.py' to run the test suite.

NB! Prior running the programm please install the 'questionary' library for Python using:

pip install questionary

## AUTHORIZATION
* Register: Create a unique username and password. 
Upon registration, the system provides option to assign you 5 "Starter Habits" (e.g. Brush Teeth, Yoga, etc.).
* Login: Access your existing account.

## FEATURES
* Mark Done: Check off an existing habit for the current period.
* Add New: Define a habit name, a description, end-date and its periodicity (Daily or Weekly).
* Edit/Delete: Modify your habit's content/duration/periodicity or delete habit entirely.
* View Analytics: Access to the analytics submenu (described below)
Note: The system allows one action per set period. You can only check off a daily habit once per day and a weekly habit once per calendar week.

### ANALYTICS
Accessed via the View Analytics menu:

* View Current Habits: Quick overview of active habits, current streaks, and time remaining until the habit expires.
* Filter by Periodicity: See all daily or all weekly habits in one list.
* Longest Streak (Overall): Reverts the longest completion streak among all habits.
* Longest Streak (Period): Reverts the longest completion streak sorted by periodicity.

## TECHNICAL OPERATIONS
The streak calculation follows strict rules:

1. Daily Streaks: A streak is maintained if the habit is completed within 24 hours of the last completion.
2. Weekly Streaks: A streak is maintained if the habit is completed once within every 7-day window (Monday to Sunday cycle).

## FILE STRUCTURE
* main.py: The entry point and UI controller.
* habit.py: Logic engine for habit objects and streak calculations.
* analytics.py: Data processing for the visualization menus.
* db.py: Database initialization and connection management.
* user.py: Authentication and user data handling.
* utils.py: Date validation and formatting tools.

## LICENSE
This project is open-source and available under the MIT License.