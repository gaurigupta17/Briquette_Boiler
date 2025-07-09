import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page config
st.set_page_config(page_title="Boiler Performance Dashboard", layout="wide")
st.title("📊 Boiler Efficiency & Parameter Dashboard")

# Upload section
st.sidebar.header("Upload Excel Files")
fuel_file = st.sidebar.file_uploader("Upload Boiler Fuel Data File", type=["xlsx"])
param_file = st.sidebar.file_uploader("Upload Boiler Parameter Data File", type=["xlsx"])

if fuel_file and param_file:
    # Load Data
    fuel_df = pd.read_excel(fuel_file)
    param_df = pd.read_excel(param_file)

    # Clean and Rename Columns
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

    # Convert both Dates to same type (date object only)
    fuel_df['Date'] = pd.to_datetime(fuel_df['Date']).dt.date
    param_df['Date'] = pd.to_datetime(param_df['Timestamp']).dt.date

    # Calculate Boiler Efficiency
    fuel_df['Boiler_Efficiency'] = (fuel_df['Steam_Generated_MT'] / fuel_df['Fuel_Consumed_MT']) * 17.5  # Approx CV for briquette * 0.9

    # Create Buckets
    bins = [0, 70, 72, 75, float('inf')]
    labels = ['<70%', '70–72%', '72–75%', '>75%']
    fuel_df['Efficiency_Bucket'] = pd.cut(fuel_df['Boiler_Efficiency'], bins=bins, labels=labels)

    # Merge
    merged_df = pd.merge(param_df, fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']],
                         how='left', on='Date')

    # Display Data
    st.subheader("Fuel Data Preview")
    st.dataframe(fuel_df.head())

    st.subheader("Boiler Parameter Data Preview")
    st.dataframe(param_df.head())

    # Grouped Mean Table
    st.subheader("Average Parameter Values by Efficiency Bucket")
    mean_table = merged_df.groupby('Efficiency_Bucket').mean(numeric_only=True).round(2)
    st.dataframe(mean_table)

    # Plot 1: Efficiency Bucket Distribution
    st.subheader("Efficiency Bucket Distribution")
    fig1, ax1 = plt.subplots()
    sns.countplot(x='Efficiency_Bucket', data=fuel_df, palette='Set2', ax=ax1)
    ax1.set_title("Count of Days by Efficiency Bucket")
    st.pyplot(fig1)

    # Plot 2: O2 vs Efficiency Trend
    st.subheader("Oxygen Level vs Boiler Efficiency")
    fig2, ax2 = plt.subplots()
    sns.lineplot(x=merged_df['Timestamp'], y=merged_df['O2_Analyser'], hue=merged_df['Efficiency_Bucket'], ax=ax2)
    ax2.set_ylabel("O2 Level")
    st.pyplot(fig2)

    # Plot 3: Steam Flow Trends
    st.subheader("Boiler Steam Flow Over Time")
    fig3, ax3 = plt.subplots()
    sns.lineplot(x='Timestamp', y='Boiler_Steam_Flow', data=merged_df, ax=ax3)
    ax3.set_title("Steam Flow Per Minute")
    st.pyplot(fig3)

else:
    st.info("Upload both Excel files to proceed.")
