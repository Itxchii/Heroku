import streamlit as st
import pandas as pd
import plotly.express as px
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process, fic_export_data, format_data_jour
import logging
import os
import glob
from datetime import datetime

def remove_data(df: pd.DataFrame, last_n_samples: int = 4*3):
    return df.iloc[:-last_n_samples]

logging.basicConfig(level=logging.INFO)

LAG_N_DAYS: int = 7

os.makedirs("data/raw/", exist_ok=True)
os.makedirs("data/interim/", exist_ok=True)

for file_path in glob.glob("data/raw/*json"):
    try:
        os.remove(file_path)
    except FileNotFoundError as e:
        logging.warning(e)

st.title("Data Visualization App")

@st.cache_data(ttl=15 * 60)
def load_data(lag_days: int):
    load_data_from_lag_to_today(lag_days)
    main_process()
    data = pd.read_csv(fic_export_data, parse_dates=[col_date])
    return data

df = load_data(LAG_N_DAYS)
df = remove_data(df, last_n_samples=4*24)

st.subheader("Line Chart of Numerical Data Over Time")
numerical_column = col_donnees

now = datetime.now()
now_aware = now.replace(microsecond=0).isoformat() + '+00:00'
formatted_time = datetime.fromisoformat(now_aware)
last = df.iloc[-1][col_date]
diff = formatted_time - last

fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)

st.subheader(f'Temps manquant: {diff}')

# Define the order of days of the week
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Map numeric day of week to day name
day_of_week_map = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

# Apply mapping to day of week column
df['day_of_week'] = (df[col_date].dt.dayofweek + 1) % 7  # Adding 1 to shift the days by one
df['day_of_week'] = df['day_of_week'].map(day_of_week_map)

# Create the bar chart with specified category order
fig2 = px.bar(df.groupby('day_of_week')[col_donnees].mean().reset_index(), 
              x='day_of_week', y=col_donnees, 
              title="Moyenne de la consommation des jours de la semaine",
              category_orders={"day_of_week": day_order})
st.plotly_chart(fig2)
