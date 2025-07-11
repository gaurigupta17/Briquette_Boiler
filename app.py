import os
os.system("pip install fpdf")
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF

# Utility to convert plot to download button
def fig_to_download(fig, filename):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button("⬇️ Download Plot", buf.getvalue(), file_name=filename, mime="image/png")

def generate_pdf_report(df_summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Boiler Report Summary", ln=True, align='C')
    
    for i, row in df_summary.iterrows():
        for col in df_summary.columns:
            line = f"{col}: {row[col]}"
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.cell(200, 5, txt="---", ln=True)
    
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

summary_df = fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Level']]
pdf_file = generate_pdf_report(summary_df)
st.download_button("⬇️ Download PDF Report", data=pdf_file, file_name="boiler_summary.pdf", mime="application/pdf")


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
    param_df['Date'] = pd.to_datetime(param_df['Timestamp']).dt.date
    param_df['Timestamp'] = pd.to_datetime(param_df['Timestamp'])
    param_df = param_df[param_df['Timestamp'].dt.time.between(pd.to_datetime("07:00:00").time(), pd.to_datetime("19:00:00").time())]

    fuel_df['Boiler_Efficiency'] = (fuel_df['Steam_Generated_MT'] / fuel_df['Fuel_Consumed_MT']) * 17.5

    # Boxplot with Quartiles (All Days)
    st.subheader("📦 Boiler Efficiency Distribution")
    st.markdown("This boxplot shows how boiler efficiency is distributed across all available days, along with quartiles.")

    efficiency_data = fuel_df['Boiler_Efficiency'].dropna().values

    q1 = np.percentile(efficiency_data, 25)

    q3 = np.percentile(efficiency_data, 75)

    fig6, ax7 = plt.subplots(figsize=(6, 4))
    sns.boxplot(y=efficiency_data, color='lightblue', ax=ax7)
    
    # Annotate Quartiles
    ax7.scatter(0, q1, color='blue', label=f"Q1: {q1:.2f}", zorder=5)
    
    ax7.scatter(0, q3, color='red', label=f"Q3: {q3:.2f}", zorder=5)
    ax7.legend(loc='upper right')
    ax7.set_ylabel("Boiler Efficiency (%)")
    ax7.set_xticks([])
    
    st.pyplot(fig6)
    fig_to_download(fig6, "boiler_efficiency_boxplot_quartiles.png")
    
    def categorize_efficiency(eff):
        if eff < q1:
            return "Low"
        elif eff <= q3:
            return "Medium"
        else:
            return "High"

    fuel_df['Efficiency_Level'] = fuel_df['Boiler_Efficiency'].apply(categorize_efficiency)

    color_map = {"Low": "red", "Medium": "orange", "High": "green"}
    colors = fuel_df['Efficiency_Level'].map(color_map)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(fuel_df['Date'].astype(str), fuel_df['Boiler_Efficiency'], color=colors)
    ax.set_title("Daily Efficiency Status by Bucket")
    ax.set_ylabel("Efficiency (%)")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    fig_to_download(fig, "daily_efficiency_status.png")

    merged_df = pd.merge(param_df, fuel_df[['Date', 'Efficiency_Level']], on='Date', how='left')

    numeric_columns = merged_df.select_dtypes(include=[np.number]).columns.difference(['Date'])
    
    for col in numeric_columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(x='Efficiency_Level', y=col, data=merged_df, palette=color_map)
        ax.set_title(f"{col} by Efficiency Level")
        st.pyplot(fig)
        fig_to_download(fig, f"{col}_boxplot.png")
    
        

 
    # Fuel Table
    st.subheader("📘 Fuel & Parameter Data Preview")
    st.markdown("This table shows all values of steam generation and fuel consumed, day-wise.")
    st.dataframe(fuel_df)
    st.download_button("⬇️ Download Fuel Data (CSV)", fuel_df.to_csv(index=False), file_name="fuel_data.csv", mime="text/csv")

    # Efficiency over time
    st.subheader("📈 Boiler Efficiency Over Time")
    st.markdown("This line chart shows how boiler efficiency has changed daily.")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.lineplot(x='Date', y='Boiler_Efficiency', data=fuel_df, marker='o', ax=ax1)
    ax1.set_ylabel("Efficiency (%)")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)
    fig_to_download(fig1, "boiler_efficiency_over_time.png")

    # Pie Chart
    st.subheader("📊 Efficiency Bucket Breakdown")
    st.markdown("Pie chart showing how many days fall into each efficiency category.")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    fuel_df['Efficiency_Bucket'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'), ax=ax2)
    ax2.set_ylabel("")
    st.pyplot(fig2)
    fig_to_download(fig2, "efficiency_bucket_pie_chart.png")

    



    # Fuel vs Steam Line
    st.subheader("🪵 Fuel vs Steam Output (Line)")
    st.markdown("This plot compares daily steam generation and fuel used.")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(fuel_df['Date'], fuel_df['Steam_Generated_MT'], color='tab:blue', label='Steam Generated')
    ax3.set_ylabel("Steam (MT)", color='tab:blue')
    ax3.tick_params(axis='y', labelcolor='tab:blue')
    ax4 = ax3.twinx()
    ax4.plot(fuel_df['Date'], fuel_df['Fuel_Consumed_MT'], color='tab:orange', label='Fuel Consumed')
    ax4.set_ylabel("Fuel (MT)", color='tab:orange')
    ax4.tick_params(axis='y', labelcolor='tab:orange')
    ax3.tick_params(axis='x', rotation=45)
    fig3.tight_layout()
    st.pyplot(fig3)
    fig_to_download(fig3, "fuel_vs_steam_line_chart.png")

    # Fuel vs Steam Bar
    st.subheader("📦 Fuel vs Steam Output (Grouped Bar)")
    st.markdown("A grouped bar chart to show daily steam output vs fuel used side-by-side.")
    fig4, ax5 = plt.subplots(figsize=(8, 4))
    width = 0.4
    x = np.arange(len(fuel_df['Date']))
    ax5.bar(x - width/2, fuel_df['Steam_Generated_MT'], width, label='Steam')
    ax5.bar(x + width/2, fuel_df['Fuel_Consumed_MT'], width, label='Fuel')
    ax5.set_xticks(x)
    ax5.set_xticklabels(fuel_df['Date'], rotation=45)
    ax5.set_ylabel("MT")
    ax5.legend()
    st.pyplot(fig4)
    fig_to_download(fig4, "fuel_vs_steam_bar_chart.png")

    # O2 Simple Bar
    st.subheader("🫧 Daily Average Oxygen Level")
    st.markdown("O₂ analyser readings shown day-wise.")
    avg_o2 = merged_df.groupby('Date')['O2_Analyser'].mean().reset_index()
    fig5, ax6 = plt.subplots(figsize=(8, 4))
    sns.barplot(x='Date', y='O2_Analyser', data=avg_o2, palette='Blues_d', ax=ax6)
    ax6.set_ylabel("O2 Level (%)")
    ax6.tick_params(axis='x', rotation=45)
    st.pyplot(fig5)
    fig_to_download(fig5, "oxygen_level_bar_chart.png")

    # Averages Table
    st.subheader("📐 Parameter Averages by Efficiency")
    st.markdown("This table helps compare boiler parameters across different efficiency levels.")
    mean_table = merged_df.groupby('Efficiency_Bucket').mean(numeric_only=True).round(2)
    st.dataframe(mean_table)
    st.download_button("⬇️ Download Averages Table (CSV)", mean_table.to_csv(), file_name="parameter_averages.csv", mime="text/csv")

    # Efficiency Status Table
    st.subheader("📅 Daily Efficiency Buckets")
    st.markdown("Shows which efficiency range each day belongs to.")
    status_table = fuel_df[['Date', 'Boiler_Efficiency', 'Efficiency_Bucket']]
    st.dataframe(status_table)
    st.download_button("⬇️ Download Efficiency Status (CSV)", status_table.to_csv(index=False), file_name="efficiency_status.csv", mime="text/csv")

else:
    st.info("Upload both Excel files to begin analysis.")
