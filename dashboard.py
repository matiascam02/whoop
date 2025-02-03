# dashboard.py

import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from whoop import WhoopClient

# --- Dashboard Title & Description ---
st.title("WHOOP Data Dashboard")
st.markdown(
    """
    This dashboard displays your WHOOP sleep and workout data over a selected date range.
    Use the sidebar to select the desired date range.
    """
)

# --- Sidebar: Date Range Selection ---
st.sidebar.header("Select Date Range")
today = datetime.today()
default_start_date = today - timedelta(days=7)
start_date = st.sidebar.date_input("Start date", default_start_date)
end_date = st.sidebar.date_input("End date", today)

if start_date > end_date:
    st.error("Error: End date must fall after start date.")
    st.stop()

# Format dates as strings in YYYY-MM-DD
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# --- Load WHOOP Credentials from .env ---
load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
if not username or not password:
    st.error("WHOOP credentials not set in the .env file.")
    st.stop()

# --- Data Fetching Function with Streamlit Caching ---
@st.cache_data(show_spinner=True)
def load_data(start_date: str, end_date: str):
    """
    Connects to the WHOOP API and retrieves sleep and workout data between the specified dates.
    """
    with WhoopClient(username, password) as client:
        sleep_data = client.get_sleep_collection(start_date, end_date)
        workout_data = client.get_workout_collection(start_date, end_date)
    return sleep_data, workout_data

sleep_collection, workout_collection = load_data(start_str, end_str)

# --- Convert Collections to Pandas DataFrames ---
if sleep_collection:
    df_sleep = pd.json_normalize(sleep_collection)
    # Convert the 'start' and 'end' fields to datetime objects
    df_sleep["start"] = pd.to_datetime(df_sleep["start"])
    df_sleep["end"] = pd.to_datetime(df_sleep["end"])
    # Calculate sleep duration in hours
    df_sleep["duration_hours"] = (df_sleep["end"] - df_sleep["start"]).dt.total_seconds() / 3600
else:
    df_sleep = pd.DataFrame()

if workout_collection:
    df_workout = pd.json_normalize(workout_collection)
    df_workout["start"] = pd.to_datetime(df_workout["start"])
else:
    df_workout = pd.DataFrame()

# --- Display Data Tables ---
st.header("Sleep Data")
if not df_sleep.empty:
    st.dataframe(df_sleep)
else:
    st.write("No sleep data available for the selected range.")

st.header("Workout Data")
if not df_workout.empty:
    st.dataframe(df_workout)
else:
    st.write("No workout data available for the selected range.")

# --- Visualizations for Sleep Data ---
if not df_sleep.empty:
    st.subheader("Sleep Duration Over Time")
    fig_duration = px.line(
        df_sleep,
        x="start",
        y="duration_hours",
        labels={"start": "Sleep Start Time", "duration_hours": "Duration (hours)"},
        title="Sleep Duration Over Time",
    )
    st.plotly_chart(fig_duration, use_container_width=True)

    # Visualize Sleep Performance Percentage (if available)
    if "score.sleep_performance_percentage" in df_sleep.columns:
        st.subheader("Sleep Performance Percentage")
        fig_performance = px.bar(
            df_sleep,
            x="start",
            y="score.sleep_performance_percentage",
            labels={"start": "Sleep Start Time", "score.sleep_performance_percentage": "Performance (%)"},
            title="Sleep Performance Percentage Over Time",
        )
        st.plotly_chart(fig_performance, use_container_width=True)
else:
    st.write("No sleep visualizations available.")

# --- Visualizations for Workout Data ---
if not df_workout.empty:
    st.subheader("Workout Strain Over Time")
    if "score.strain" in df_workout.columns:
        fig_strain = px.line(
            df_workout,
            x="start",
            y="score.strain",
            labels={"start": "Workout Start Time", "score.strain": "Strain"},
            title="Workout Strain Over Time",
        )
        st.plotly_chart(fig_strain, use_container_width=True)
    
    # Visualize Average Heart Rate in Workouts (if available)
    if "score.average_heart_rate" in df_workout.columns:
        st.subheader("Average Heart Rate During Workouts")
        fig_hr = px.line(
            df_workout,
            x="start",
            y="score.average_heart_rate",
            labels={"start": "Workout Start Time", "score.average_heart_rate": "Average Heart Rate"},
            title="Average Heart Rate During Workouts",
        )
        st.plotly_chart(fig_hr, use_container_width=True)
else:
    st.write("No workout visualizations available.")

# --- Additional Insights (Optional) ---
st.header("Additional Insights")
st.markdown(
    """
    You can extend this dashboard by adding more charts such as:
    - Sleep Efficiency and consistency over time.
    - Comparison of workout metrics (e.g., max heart rate, kilojoules burned).
    - Recovery scores associated with each sleep cycle.
    
    Explore the WHOOP API documentation to see all available endpoints and data fields.
    """
)