import streamlit as st
import pandas as pd

 
# import matplotlib.pyplot as plt
import plotly.express as px
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process, fic_export_data, format_data_jour
import logging
import os
import glob
from datetime import datetime
from schedule import every, repeat
import schedule
LENGTH_DATA: int = 0
 
def remove_data(df: pd.DataFrame, last_n_samples: int = 4*3):
 
    # df: pd.DataFrame = pd.read_csv(fic_export_data)
    return df.iloc[:-last_n_samples]
    # df.to_csv(fic_export_data, index=False)
logging.basicConfig(level=logging.INFO)
 
 
LAG_N_DAYS: int = 7
 
# * INIT REPO FOR DATA
os.makedirs("data/raw/", exist_ok=True)
os.makedirs("data/interim/", exist_ok=True)
 
# * remove outdated json files
for file_path in glob.glob("data/raw/*json"):
    try:
        os.remove(file_path)
    except FileNotFoundError as e:
        logging.warning(e)
 
# plt.switch_backend("TkAgg")
 
# Title for your app
st.title("Data Visualization App")
 
 
# Load data from CSV
@st.cache_data(
    ttl=15 * 60
)  # This decorator caches the data to prevent reloading on every interaction.
def load_data(lag_days: int):
    load_data_from_lag_to_today(lag_days)
    main_process()
    data = pd.read_csv(
        fic_export_data, parse_dates=[col_date]
    )  # Adjust 'DateColumn' to your date column name*
    return data
 
 
# Assuming your CSV is named 'data.csv' and is in the same directory as your app.py
df = load_data(LAG_N_DAYS)
df = remove_data(df, last_n_samples=4*24)
 
# Creating a line chart
st.subheader("Line Chart of Numerical Data Over Time")
 
# Select the numerical column to plot
# This lets the user select a column if there are multiple numerical columns available
# numerical_column = st.selectbox('Select the column to visualize:', df.select_dtypes(include=['float', 'int']).columns)
numerical_column = col_donnees
 
# ! Matplotlib - Create the plot
# fig, ax = plt.subplots()
# ax.plot(df[col_date], df[numerical_column])  # Adjust 'DateColumn' to your date column name
# ax.set_xlabel('Time')
# ax.set_ylabel(numerical_column)
# ax.set_title(f'Time Series Plot of {numerical_column}')
# # Display the plot
# st.pyplot(fig)
 
now = datetime.now()
now_aware = now.replace(microsecond=0).isoformat() + '+00:00'
formatted_time = datetime.fromisoformat(now_aware)
last = df.iloc[-1][col_date]
 
diff = formatted_time - last
 
 
# ! Plotly
# Create interactive line chart using Plotly
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)
 
st.subheader(f'Temps manquants: {diff}')
 
day_of_week_map = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}
df['day_of_week'] = df[col_date].dt.dayofweek.map(day_of_week_map)
 
fig2 = px.bar(df.groupby('day_of_week')[col_donnees].mean().reset_index(), x='day_of_week', y=col_donnees, title="Moyenne de la consommation des jours de la semaine")
st.plotly_chart(fig2)
while True:
    schedule.run_pending()
    df: pd.DataFrame = pd.read_csv(fic_export_data, parse_dates=[col_date])
    if len(df) > LENGTH_DATA:
        LENGTH_DATA = len(df)
        logging.info(f"Nb points de mesure: {LENGTH_DATA}")
        st.toast("Nouvelles données disponibles", icon="🎉")
    time.sleep(60)