# main.py

import os
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from whoop import WhoopClient

def main():
    # Load credentials from .env
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    
    if not username or not password:
        print("Please set your WHOOP USERNAME and PASSWORD in the .env file.")
        return

    # Use a context manager for the WhoopClient so that it authenticates and cleans up automatically.
    with WhoopClient(username, password) as client:
        
        # --- Example 1: Get the User Profile ---
        profile = client.get_profile()
        print("User Profile:")
        print(profile)
        print("-" * 50)
        
        # --- Example 2: Get Sleep Data for the Last 7 Days ---
        # Define the start and end dates (ISO 8601 format: YYYY-MM-DD)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=7)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        sleep_collection = client.get_sleep_collection(start_str, end_str)
        print(f"Sleep Data from {start_str} to {end_str}:")
        print(sleep_collection)
        print("-" * 50)
        
        # Convert the sleep data to a Pandas DataFrame for analysis
        if sleep_collection:
            df_sleep = pd.json_normalize(sleep_collection)
            print("Sleep Data as DataFrame:")
            print(df_sleep.head())
        else:
            print("No sleep data returned for this period.")
        print("-" * 50)
        
        # --- Example 3: Get Workout Data ---
        workout_collection = client.get_workout_collection(start_str, end_str)
        print(f"Workout Data from {start_str} to {end_str}:")
        print(workout_collection)
        # You can also normalize the workout data using Pandas if needed:
        if workout_collection:
            df_workout = pd.json_normalize(workout_collection)
            print("Workout Data as DataFrame:")
            print(df_workout.head())
        else:
            print("No workout data returned for this period.")

if __name__ == '__main__':
    main()