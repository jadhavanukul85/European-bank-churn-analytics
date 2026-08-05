import streamlit as st
import pandas as pd
import plotly.express as px
from src.analytics import load_and_preprocess_data, calculate_kpis

# Page Configuration
st.set_page_config(
    page_title="European Bank Churn Analytics",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 European Banking Customer Segmentation & Churn Analytics")
st.markdown("---")

# Load Data
@st.cache_data
def get_data():
    return load_and_preprocess_data('data/Bank_Customer_Churn.csv')

try:
    df_raw = get_data()
except Exception as e:
    st.error(f"Error loading dataset from data/Bank_Customer_Churn.csv: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔍 Global Segment Filters")

selected_geo = st.sidebar.multiselect(
    "Geography", 
    options=df_raw['Geography'].unique(), 
    default=df_raw['Geography'].unique()
)

selected_gender = st.sidebar.multiselect(
    "Gender", 
    options=df_raw['Gender'].unique(), 
    default=df_raw['Gender'].unique()
)

selected_age = st.sidebar.multiselect(
    "Age Group", 
    options=['<30', '30–45', '46–60', '60+'], 
    default=['<30', '30–45', '46–60', '60+']
)

# Apply Filters
df = df_raw[
    (df_raw['Geography'].isin(selected_geo)) &
    (df_raw['Gender'].isin(selected_gender)) &
    (df_raw['AgeGroup'].isin(selected_age))
]

# Calculate KPIs
kpis = calculate_kpis(df)

# Top KPI Metric Banner
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Customers", f"{total_customers:,}", help="Total number of bank account holders analyzed.")

with col2:
    st.metric("Overall Churn Rate", f"{overall_churn_rate:.1f}%", help="Percentage of total customers who left the bank.")

with col3:
    st.metric("High-Value Churn Rate", f"{hv_churn_rate:.1f}%", help="Churn rate for customers with balance > €100k.")

with col4:
    st.metric("Inactive Member Churn", f"{inactive_churn_rate:.1f}%", help="Churn rate among inactive accounts.")

with col5:
    st.metric("Capital at Risk (€)", f"€{capital_at_risk:,.0f}", help="Total account balance lost to high-value customer churn.")

st.markdown("---")

# Visual Analytics Section
tab1, tab2, tab3 = st.tabs(["🌍 Geography & Demographics", "📊 Product & Balance Analytics", "📋 Customer Data Explorer"])

with tab1:
    st.subheader("Geographic & Demographic Attrition Patterns")
    c1, c2 = st.columns(2)
    
    geo_churn = df.groupby('Geography')['Exited'].mean().reset_index()
    geo_churn['ChurnRate'] = geo_churn['Exited'] * 100
    fig_geo = px.bar(
        geo_churn, 
        x='Geography', 
        y='ChurnRate', 
        color='Geography',
        title="Churn Rate (%) by Country",
        text_auto='.1f'
    )
    c1.plotly_chart(fig_geo, use_container_width=True)
    
    age_churn = df.groupby(['AgeGroup', 'Gender'])['Exited'].mean().reset_index()
    age_churn['ChurnRate'] = age_churn['Exited'] * 100
    fig_age = px.bar(
        age_churn, 
        x='AgeGroup', 
        y='ChurnRate', 
        color='Gender', 
        barmode='group',
        title="Churn Rate by Age Group & Gender (%)"
    )
    c2.plotly_chart(fig_age, use_container_width=True)

with tab2:
    st.subheader("Financial Profile & Product Engagement Risk")
    c1, c2 = st.columns(2)
    
    prod_churn = df.groupby('NumOfProducts')['Exited'].mean().reset_index()
    prod_churn['ChurnRate'] = prod_churn['Exited'] * 100
    fig_prod = px.bar(
        prod_churn, 
        x='NumOfProducts', 
        y='ChurnRate', 
        title="Churn Rate (%) by Number of Bank Products",
        text_auto='.1f'
    )
    c1.plotly_chart(fig_prod, use_container_width=True)
    
    fig_scatter = px.scatter(
        df, 
        x='EstimatedSalary', 
        y='Balance', 
        color='Exited',
        color_continuous_scale=['#2ecc71', '#e74c3c'],
        title="Salary vs. Balance Distribution (Red = Churned)"
    )
    c2.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Filtered Customer-Level Drill-down")
    st.dataframe(df[['CustomerId', 'Geography', 'Gender', 'Age', 'Balance', 'NumOfProducts', 'IsActiveMember', 'Exited']])
