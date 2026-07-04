# Boiler Efficiency Dashboard

A Python-based data analysis and visualization project that evaluates the operational efficiency of a briquette-fired industrial boiler using daily steam generation and fuel consumption data. The dashboard automates efficiency calculations, identifies performance trends, and provides actionable insights through interactive visualizations.

## Overview

Industrial boilers often experience efficiency losses due to fuel quality variations, scaling, and operational inconsistencies. This project analyzes historical operational data to calculate daily boiler efficiency, visualize key performance metrics, and support data-driven maintenance decisions.

## Features

- Automated boiler efficiency calculation
- Daily steam generation and fuel consumption analysis
- Performance trend visualization
- Efficiency categorization and reporting
- Interactive dashboard for operational insights
- Data preprocessing and validation

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit
- Excel

## Dataset

The project uses operational boiler data containing:

- Steam generated (kg/day)
- Briquette fuel consumption (kg/day)
- Boiler operating parameters
- Daily production records

> **Note:** The dataset is proprietary and has not been included in this repository.

## Boiler Efficiency Formula

The efficiency is calculated using the standard heat balance approach:

```
Boiler Efficiency (%) =
(Steam Generated × Enthalpy Difference)
---------------------------------------- × 100
(Fuel Consumed × Calorific Value)
```

The formula can be modified depending on available operational parameters.

## Project Structure

```
Boiler-Efficiency-Dashboard/
│
├── data/
│   ├── fuel_data.xlsx
│   └── parameter_data.xlsx
│
├── dashboard.py
├── preprocessing.py
├── efficiency_calculator.py
├── visualization.py
├── requirements.txt
└── README.md
```

## Dashboard Insights

The dashboard provides:

- Daily boiler efficiency
- Steam generation trends
- Fuel consumption trends
- Efficiency distribution
- Monthly performance comparison
- Performance reports

## Workflow

1. Load operational datasets.
2. Clean and preprocess missing values.
3. Calculate daily boiler efficiency.
4. Generate performance metrics.
5. Visualize trends and efficiency reports.
6. Support maintenance planning through data insights.

## Future Improvements

- Machine learning model for cleaning interval prediction
- Real-time IoT sensor integration
- Automatic anomaly detection
- Predictive maintenance alerts
- Power BI integration
- SQL database connectivity

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/Boiler-Efficiency-Dashboard.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard.py
```

## Results

The dashboard automates manual efficiency calculations and enables engineers to:

- Monitor boiler performance
- Detect efficiency degradation
- Analyze fuel utilization
- Make informed maintenance decisions

## Author

**Gauri Gupta**

Integrated M.Tech Mathematics & Data Science  
National Institute of Technology (MANIT), Bhopal
