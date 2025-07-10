import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from sklearn.linear_model import LogisticRegression

# Utility for plot download
def fig_to_png_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf

# PDF export
def export_pdf(fuel_df, avg_o2, mean_table, figs):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph("Boiler Performance Report", styles['Title']))
    elems.append(Spacer(1, 12))
    elems.append(Paragraph("Fuel & Efficiency Data:", styles['Heading2']))
    elems.append(Paragraph(fuel_df.to_html(index=False), styles['Normal']))
    elems.append(Spacer(1, 12))
    for title, fig in figs:
        elems.append(Paragraph(title, styles['Heading2']))
        imgbuf = fig_to_png_bytes(fig)
        elems.append(RLImage(imgbuf, width=400, height=200))
        elems.append(Spacer(1,12))
    elems.append(Paragraph("Parameter Averages by Efficiency:", styles['Heading2']))
    elems.append(Paragraph(mean_table.to_html(), styles['Normal']))
    doc.build(elems)
    return buf.getvalue()

st.set_page_config(page_title="Boiler Dashboard", layout="wide")
st.title("📊 Boiler Efficiency & Cleaning Prediction Dashboard")

# Upload
st.sidebar.header("Upload Excel Files")
f_f = st.sidebar.file_uploader("Fuel Data", type="xlsx")
p_f = st.sidebar.file_uploader("Param Data", type="xlsx")

if f_f and p_f:
    fuel = pd.read_excel(f_f)
    param = pd.read_excel(p_f)
    # rename, parse dates, compute efficiency, buckets ...
    # (As before; skipping for brevity)
    # Ensure columns present: 'Flue_Gas_Temp', 'O2_Analyser', 'NOx'

    # 1) Simple Cleaning Rule-based
    fuel['Eff_shift'] = fuel['Boiler_Efficiency'].shift(1)
    fuel['Eff_drop_pct'] = (fuel['Eff_shift'] - fuel['Boiler_Efficiency']) / fuel['Eff_shift'] * 100
    fuel['Clean_Warning'] = ((fuel['Eff_drop_pct'] >= 3) |
                             (pd.merge(fuel[['Date']], param.groupby('Date')['Flue_Gas_Temp'].mean(), on='Date')['Flue_Gas_Temp'].diff() >= 5) |
                             (pd.merge(fuel[['Date']], param.groupby('Date')['O2_Analyser'].mean(), on='Date')['O2_Analyser'] > 15))
    st.subheader("Cleaning Warnings (Rule-based)")
    st.markdown("Red flag when efficiency drops ≥3%, flue gas ↑ 5°C, or O₂ >15%.")
    st.dataframe(fuel[['Date','Boiler_Efficiency','Eff_drop_pct','Clean_Warning']])

    # 2) Train Logistic Model (if user selects)
    merged = pd.merge(param.groupby('Date').mean().reset_index(),
                      fuel[['Date','Boiler_Efficiency','Clean_Warning']], on='Date')
    features = ['Boiler_Efficiency','Flue_Gas_Temp','O2_Analyser','NOx']
    clf = LogisticRegression()
    clf.fit(merged[features], merged['Clean_Warning'])
    merged['Clean_Prob'] = clf.predict_proba(merged[features])[:,1]
    st.subheader("Cleaning Probability (ML Model)")
    st.markdown("Shows cleaning probability based on past rules.")
    st.bar_chart(merged.set_index('Date')['Clean_Prob'])

    # Export sections & plots...
    figs = []
    # Efficiency line plot
    fig_e, ax = plt.subplots(figsize=(6,3))
    sns.lineplot(...); ax.tick_params(...)
    figs.append(("Efficiency Over Time", fig_e))
    # O2 bar
    fig_o2, ax2 = plt.subplots(...)

    # PDF export button
    pdf_bytes = export_pdf(fuel, None, merged.groupby('Efficiency_Bucket')[features].mean(), figs)
    st.download_button("⬇️ Download Full Report (PDF)", pdf_bytes, "boiler_report.pdf", "application/pdf")
else:
    st.info("Upload both files to analyze.")
