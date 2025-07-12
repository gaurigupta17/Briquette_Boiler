import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Utility to convert plot to download button
def fig_to_download(fig, filename):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button("⬇️ Download Plot", buf.getvalue(), file_name=filename, mime="image/png")

# Streamlit config
st.set_page_config(page_title="Boiler Dashboard", layout="wide")
st.title("📊 Boiler Efficiency & Parameter Dashboard")

# Uploads
st.sidebar.header("Upload Excel Files")
fuel_file = st.sidebar.file_uploader("Upload Boiler Fuel Data File", type=["xlsx"])
param_file = st.sidebar.file_uploader("Upload Boiler Parameter Data File", type=["xlsx"])

if fuel_file and param_file:
    fuel_df = pd.read_excel(fuel_file)
    param_df = pd.read_excel(param_file)

    # Rename columns
    fuel_df.rename(columns={
        'Qty. of Steam Generated (in MT)': 'Steam_Generated_MT',
        'Fuel Consumed (in MT)': 'Fuel_Consumed_MT'
    }, inplace=True)

    param_df.rename(columns={
        'dateandtime': 'Timestamp',
        'EquipmentName': 'BoilerName',
        'AT_704A_Sox_Analyser': 'SOx',
        'AT_704B_Nox_Analyser': 'NOx',
        'AT_706_SPM_Analyser': 'SPM',
        'FIQ_601_Boiler_Steam_Flow_Totaliser': 'Boiler_Steam_Total',
        'FIQ_603_Deaerator_Steam_Flow_Totaliser': 'Deaerator_Steam_Total',
        'FT_601A_Boiler_Outlet_Steam_Flow': 'Boiler_Steam_Flow',
        'FT_603_Deaerator_Steam_Flow': 'Deaerator_Steam_Flow',
        'LT_501_Deaerator_Tank_Level': 'Deaerator_Tank_Level',
        'LT_601_Boiler_Water_Level': 'Boiler_Water_Level',
        'PIC_401A_RAMP_OP_Id_Fan_VFD_Speed_Control_Signal': 'IDFan_Speed_Signal',
        'PT_401A_Furnace_Draft_Pressure': 'Furnace_Draft',
        'PT_601_Boiler_Steam_Pressure': 'Steam_Pressure',
        'TE_208_Steam_Header_Temp': 'Steam_Header_Temp',
        'TE_401A_Furnace_Exit_Temp_1': 'Furnace_Exit_Temp_1',
        'TE_401C_Furnace_Exit_Temp_2': 'Furnace_Exit_Temp_2',
        'TE_402_Boiler_Outlet_Flue_Gas_Temp': 'Flue_Gas_Temp',
        'TE_501_Economiser_Inlet_Water_Temp': 'Eco_Inlet_Water_Temp',
        'TE_502_Economiser_Outlet_Water_Temp': 'Eco_Outlet_Water_Temp',
        'XT_301A_Primary_Air_Damper_1': 'PA_Damper_1',
        'XT_301B_Primary_Air_Damper_2': 'PA_Damper_2',
        'XT_301C_Primary_Air_Damper_3': 'PA_Damper_3',
        'XT_302A_Secondary_Air_Damper_1': 'SA_Damper_1',
        'XT_302B_Secondary_Air_Damper_2': 'SA_Damper_2',
        'AT_401_Oxygen_Analyser': 'O2_Analyser',
        'BoilerOnOffStatus': 'Boiler_Status'
    }, inplace=True)

    fuel_df['Date'] = pd.to_datetime(fuel_df['Date']).dt.date
    param_df['Timestamp'] = pd.to_datetime(param_df['Timestamp'])
    param_df = param_df[param_df['Timestamp'].dt.time.between(pd.to_datetime("07:00:00").time(), pd.to_datetime("19:00:00").time())]
    param_df['Date'] = param_df['Timestamp'].dt.date

    # Calculate Boiler Efficiency using updated constants
    fuel_df['Boiler_Efficiency'] = (fuel_df['Steam_Generated_MT'] * 610) / (fuel_df['Fuel_Consumed_MT'] * 3600) * 100

    # Quartile Boxplot
    st.subheader("📦 Boiler Efficiency Distribution")
    efficiency_data = fuel_df['Boiler_Efficiency'].dropna().values
    q1 = np.percentile(efficiency_data, 25)
    q3 = np.percentile(efficiency_data, 75)
    fig_q, ax_q = plt.subplots(figsize=(6, 4))
    sns.boxplot(y=efficiency_data, color='lightblue', ax=ax_q)
    ax_q.scatter(0, q1, color='blue', label=f"Q1: {q1:.2f}", zorder=5)
    ax_q.scatter(0, q3, color='red', label=f"Q3: {q3:.2f}", zorder=5)
    ax_q.legend(loc='upper right')
    ax_q.set_ylabel("Boiler Efficiency (%)")
    ax_q.set_xticks([])
    st.pyplot(fig_q)
    fig_to_download(fig_q, "efficiency_quartiles_boxplot.png")

    # Efficiency bucketing
    def bucket_efficiency(eff):
        if eff < 68:
            return "<68%"
        elif eff <= 70:
            return "68%-70%"
        else:
            return ">70%"

    fuel_df['Efficiency_Bucket'] = fuel_df['Boiler_Efficiency'].apply(bucket_efficiency)

    # Colored Barplot for Efficiency Bucket
    st.subheader("📊 Daily Efficiency Buckets")
    color_map = {
        "Less than 68%": "red",
        "Between 68% and 70%": "orange",
        "More than 70%": "green"
    }
    colors = fuel_df['Efficiency_Bucket'].map(color_map).fillna("grey")

    fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
    ax_bar.bar(fuel_df['Date'].astype(str), fuel_df['Boiler_Efficiency'], color=colors)
    ax_bar.set_ylabel("Efficiency (%)")
    ax_bar.tick_params(axis='x', rotation=45)
    st.pyplot(fig_bar)
    fig_to_download(fig_bar, "daily_efficiency_buckets_colored.png")

    # Merge with parameters
    merged_df = pd.merge(param_df, fuel_df[['Date', 'Efficiency_Bucket']], on='Date', how='left')

    # Parameter-wise Boxplots (New Buckets)
    st.subheader("📦 Parameter Variation by Efficiency Bucket")
    numeric_cols = merged_df.select_dtypes(include=np.number).columns.difference(['Date'])
    for col in numeric_cols:
        fig_b, ax_b = plt.subplots(figsize=(5, 3))
        sns.boxplot(data=merged_df, x='Efficiency_Bucket', y=col, palette=color_map, ax=ax_b)
        ax_b.set_title(f"{col}")
        st.pyplot(fig_b)
        fig_to_download(fig_b, f"{col}_efficiency_bucket_boxplot.png")

    # Efficiency Trend
    st.subheader("📈 Boiler Efficiency Over Time")
    fig_trend, ax_trend = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=fuel_df, x='Date', y='Boiler_Efficiency', marker='o', ax=ax_trend)
    ax_trend.set_ylabel("Efficiency (%)")
    ax_trend.tick_params(axis='x', rotation=45)
    st.pyplot(fig_trend)
    fig_to_download(fig_trend, "efficiency_over_time.png")

    # O2 Levels
    st.subheader("🫧 Daily Average Oxygen Level")
    avg_o2 = merged_df.groupby('Date')['O2_Analyser'].mean().reset_index()
    fig_o2, ax_o2 = plt.subplots(figsize=(8, 4))
    sns.barplot(data=avg_o2, x='Date', y='O2_Analyser', palette='Blues_d', ax=ax_o2)
    ax_o2.set_ylabel("O2 Level (%)")
    ax_o2.tick_params(axis='x', rotation=45)
    st.pyplot(fig_o2)
    fig_to_download(fig_o2, "oxygen_level_bar_chart.png")

    # Steam vs Fuel - Line
    st.subheader("🪵 Steam vs Fuel (Line Chart)")
    fig_sf, ax_sf = plt.subplots(figsize=(8, 4))
    ax_sf.plot(fuel_df['Date'], fuel_df['Steam_Generated_MT'], label='Steam Generated', color='blue')
    ax_sf.set_ylabel("Steam (MT)", color='blue')
    ax_sf.tick_params(axis='y', labelcolor='blue')
    ax2 = ax_sf.twinx()
    ax2.plot(fuel_df['Date'], fuel_df['Fuel_Consumed_MT'], label='Fuel Consumed', color='orange')
    ax2.set_ylabel("Fuel (MT)", color='orange')
    ax_sf.tick_params(axis='x', rotation=45)
    st.pyplot(fig_sf)
    fig_to_download(fig_sf, "steam_vs_fuel_line.png")

    # Steam vs Fuel - Grouped Bar
    st.subheader("📦 Steam vs Fuel (Bar Chart)")
    fig_gb, ax_gb = plt.subplots(figsize=(8, 4))
    x = np.arange(len(fuel_df))
    width = 0.4
    ax_gb.bar(x - width/2, fuel_df['Steam_Generated_MT'], width, label='Steam')
    ax_gb.bar(x + width/2, fuel_df['Fuel_Consumed_MT'], width, label='Fuel')
    ax_gb.set_xticks(x)
    ax_gb.set_xticklabels(fuel_df['Date'], rotation=45)
    ax_gb.set_ylabel("MT")
    ax_gb.legend()
    st.pyplot(fig_gb)
    fig_to_download(fig_gb, "steam_vs_fuel_bar.png")

    # Data Tables
    st.subheader("📘 Fuel Data Table")
    st.dataframe(fuel_df)
    st.download_button("⬇️ Download Fuel Data", fuel_df.to_csv(index=False), "fuel_data.csv")

    st.subheader("📐 Parameter Averages by Efficiency")
    avg_table = merged_df.groupby('Efficiency_Bucket').mean(numeric_only=True).round(2)
    st.dataframe(avg_table)
    st.download_button("⬇️ Download Parameter Averages", avg_table.to_csv(), "parameter_averages.csv")

    st.subheader("📅 Daily Efficiency Status")
    status_table = fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']]
    st.dataframe(status_table)
    st.download_button("⬇️ Download Efficiency Status", status_table.to_csv(index=False), "efficiency_status.csv")

else:
    st.info("Upload both Excel files to begin analysis.")
