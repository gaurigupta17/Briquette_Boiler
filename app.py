import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Boiler Performance Dashboard", layout="wide")
st.title("📊 Boiler Efficiency & Parameter Dashboard")

# Upload section
st.sidebar.header("Upload Excel Files")
fuel_file = st.sidebar.file_uploader("Upload Boiler Fuel Data File", type=["xlsx"])
param_file = st.sidebar.file_uploader("Upload Boiler Parameter Data File", type=["xlsx"])

if fuel_file and param_file:
    fuel_df = pd.read_excel(fuel_file)
    param_df = pd.read_excel(param_file)

    # Rename Columns
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
    param_df['Date'] = pd.to_datetime(param_df['Timestamp']).dt.date

    fuel_df['Boiler_Efficiency'] = (fuel_df['Steam_Generated_MT'] / fuel_df['Fuel_Consumed_MT']) * 17.5

    bins = [0, 70, 72, 75, float('inf')]
    labels = ['<70%', '70–72%', '72–75%', '>75%']
    fuel_df['Efficiency_Bucket'] = pd.cut(fuel_df['Boiler_Efficiency'], bins=bins, labels=labels)

    merged_df = pd.merge(param_df, fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']], on='Date', how='left')

    st.subheader("1️⃣ Fuel & Parameter Data Preview")
    st.dataframe(fuel_df.head())
    st.dataframe(param_df.head())

    st.subheader("2️⃣ Boiler Efficiency Over Time")
    fig, ax = plt.subplots()
    daily_eff = fuel_df.groupby('Date')['Boiler_Efficiency'].mean()
    daily_eff.plot(ax=ax, marker='o')
    ax.set_title("Boiler Efficiency Over Time")
    ax.set_ylabel("Efficiency (%)")
    st.pyplot(fig)

    st.subheader("3️⃣ Efficiency Bucket Breakdown (Pie Chart)")
    pie_data = fuel_df['Efficiency_Bucket'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
    ax.set_title("Efficiency Bucket Distribution")
    st.pyplot(fig)

    st.subheader("4️⃣ Daily Efficiency Status")
    status_df = fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']]
    st.dataframe(status_df)

    st.subheader("5️⃣ Oxygen Level vs Boiler Efficiency")
    fig, ax = plt.subplots()
    sns.scatterplot(x='Boiler_Efficiency', y='O2_Analyser', data=merged_df, hue='Efficiency_Bucket', palette='Set1')
    ax.set_title("O2 vs Efficiency")
    ax.set_xlabel("Boiler Efficiency")
    ax.set_ylabel("O2 Level")
    st.pyplot(fig)

    st.subheader("6️⃣ Steam Flow Over Time")
    fig, ax = plt.subplots()
    sns.lineplot(x='Timestamp', y='Boiler_Steam_Flow', data=merged_df, ax=ax)
    ax.set_title("Boiler Steam Flow Per Minute")
    st.pyplot(fig)

    st.subheader("7️⃣ Fuel vs Steam Output - Dual Axis Line")
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    fuel_grouped = fuel_df.groupby('Date').agg({'Fuel_Consumed_MT': 'sum', 'Steam_Generated_MT': 'sum'})
    ax1.plot(fuel_grouped.index, fuel_grouped['Fuel_Consumed_MT'], color='r', label='Fuel Used')
    ax2.plot(fuel_grouped.index, fuel_grouped['Steam_Generated_MT'], color='b', label='Steam Generated')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Fuel Consumed (MT)", color='r')
    ax2.set_ylabel("Steam Generated (MT)", color='b')
    st.pyplot(fig)

    st.subheader("8️⃣ Fuel vs Steam Output - Grouped Bar Chart")
    fig, ax = plt.subplots()
    fuel_grouped[['Fuel_Consumed_MT', 'Steam_Generated_MT']].plot(kind='bar', ax=ax)
    ax.set_title("Daily Fuel vs Steam Output")
    ax.set_ylabel("MT")
    st.pyplot(fig)

    st.subheader("9️⃣ Average Parameter Values by Efficiency Bucket")
    avg_table = merged_df.groupby('Efficiency_Bucket').mean(numeric_only=True).round(2)
    st.dataframe(avg_table)

else:
    st.info("Upload both Excel files to proceed.")
