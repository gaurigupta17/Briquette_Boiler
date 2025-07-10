import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# Set Streamlit page config
st.set_page_config(page_title="Boiler Performance Dashboard", layout="wide")
st.title("\U0001F4CA Boiler Efficiency & Parameter Dashboard")

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
    fuel_df['Boiler_Efficiency'] = (fuel_df['Steam_Generated_MT'] / fuel_df['Fuel_Consumed_MT']) * 17.5

    # Create Buckets
    bins = [0, 70, 72, 75, float('inf')]
    labels = ['<70%', '70–72%', '72–75%', '>75%']
    fuel_df['Efficiency_Bucket'] = pd.cut(fuel_df['Boiler_Efficiency'], bins=bins, labels=labels)

    # Merge
    merged_df = pd.merge(param_df, fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']], how='left', on='Date')

    # Display full Fuel Data
    st.subheader("1. Fuel & Parameter Data Preview")
    st.write("Full table showing daily fuel and steam values for easy reference.")
    st.dataframe(fuel_df)

    # Boiler Efficiency Over Time
    st.subheader("2. Daily Boiler Efficiency Over Time")
    st.write("This line chart tracks how the boiler efficiency varies daily.")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=fuel_df['Date'], y=fuel_df['Boiler_Efficiency'], marker='o', ax=ax)
    ax.set_xticks(ax.get_xticks()[::2])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_ylabel("Efficiency (%)")
    ax.set_xlabel("Date")
    st.pyplot(fig)

    # Efficiency Bucket Pie Chart
    st.subheader("3. Efficiency Bucket Breakdown")
    st.write("Pie chart to show the proportion of days falling in each efficiency range.")
    fig, ax = plt.subplots(figsize=(6, 4))
    fuel_df['Efficiency_Bucket'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, ax=ax, colors=sns.color_palette("Set2"))
    ax.set_ylabel("")
    st.pyplot(fig)

    # O2 vs Efficiency Bucket Boxplot
    st.subheader("4. Oxygen Level vs Efficiency Bucket")
    st.write("Boxplot showing average oxygen level across efficiency ranges. More readable than scatter.")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=merged_df, x='Efficiency_Bucket', y='O2_Analyser', palette="Set2", ax=ax)
    st.pyplot(fig)

    # Steam Flow Over Time
    st.subheader("5. Boiler Steam Flow Over Time")
    st.write("Line chart representing steam flow trends during operations.")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=merged_df, x='Timestamp', y='Boiler_Steam_Flow', ax=ax)
    ax.set_xticks(ax.get_xticks()[::6])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title("Boiler Steam Flow Per Minute")
    st.pyplot(fig)

    # Daily Fuel vs Steam Output - Dual Axis
    st.subheader("6. Daily Fuel vs Steam Output (Dual Axis Line Chart)")
    st.write("Shows relationship between steam produced and fuel used over time.")
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2 = ax1.twinx()
    ax1.plot(fuel_df['Date'], fuel_df['Steam_Generated_MT'], color='tab:blue', label='Steam')
    ax2.plot(fuel_df['Date'], fuel_df['Fuel_Consumed_MT'], color='tab:red', label='Fuel')
    ax1.set_xticks(ax1.get_xticks()[::2])
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
    ax1.set_ylabel("Steam Generated (MT)")
    ax2.set_ylabel("Fuel Consumed (MT)")
    st.pyplot(fig)

    # Daily Fuel vs Steam Output - Grouped Bar Chart
    st.subheader("7. Daily Fuel vs Steam Output (Bar Chart)")
    st.write("Bar chart comparing fuel and steam values for each day side-by-side.")
    fig, ax = plt.subplots(figsize=(8, 4))
    width = 0.4
    x = np.arange(len(fuel_df['Date']))
    ax.bar(x - width/2, fuel_df['Steam_Generated_MT'], width=width, label='Steam')
    ax.bar(x + width/2, fuel_df['Fuel_Consumed_MT'], width=width, label='Fuel')
    ax.set_xticks(x[::2])
    ax.set_xticklabels([str(d) for d in fuel_df['Date']][::2], rotation=45)
    ax.legend()
    st.pyplot(fig)

    # Table: Parameter Averages by Efficiency Bucket
    st.subheader("8. Parameter Averages by Efficiency Bucket")
    st.write("Displays how key parameters change as efficiency varies.")
    mean_table = merged_df.groupby('Efficiency_Bucket').mean(numeric_only=True).round(2)
    st.dataframe(mean_table)

    # Daily Efficiency Status (Bar Chart)
    st.subheader("9. Daily Efficiency Buckets")
    st.write("Quick visual of how many days fall in each efficiency category.")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(x='Efficiency_Bucket', data=fuel_df, palette='Set2', ax=ax)
    ax.set_title("Count of Days by Efficiency Bucket")
    st.pyplot(fig)

else:
    st.info("Upload both Excel files to proceed.")
