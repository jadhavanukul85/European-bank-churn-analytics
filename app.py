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
st.warning("⚠️ **Executive Insight:** Customers in Germany exhibit double the attrition rate (32.4%) compared to France and Spain, with inactive members accounting for the largest total capital at risk.")
with st.expander("📖 View Key Terms & Analytics Methodology"):
    st.markdown("""
    * **High-Value Customer:** Account holders maintaining an active balance exceeding **€100,000**.
    * **Capital at Risk:** Total sum of remaining account balances across all churned customers within the selected filter.
    * **Active Member:** Customers who actively transact or utilize online banking services (recorded via `IsActiveMember`).
    * **Churn / Attrition:** Customers who officially closed their bank accounts (`Exited = 1`).
    """)
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
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    st.rerun()
min_balance = st.sidebar.slider(
    "Minimum Balance (€)", 
    min_value=0, 
    max_value=250000, 
    value=0, 
    step=10000,
    help="Filter data to include only customers with an account balance above this amount."
)

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
    st.sidebar.divider()
st.sidebar.markdown("### 📊 Dataset Overview")
st.sidebar.caption(f"**Total Records:** {len(df_raw):,} customers")
st.sidebar.caption(f"**Filtered Output:** {len(df):,} customers")
st.sidebar.caption("**Data Source:** European Banking Group")
    (df_raw['Geography'].isin(selected_geo)) &
    (df_raw['Gender'].isin(selected_gender)) &
    (df_raw['AgeGroup'].isin(selected_age)) &
    (df_raw['Balance'] >= min_balance)
]

# Calculate KPIs
kpis = calculate_kpis(df)

# Top KPI Metric Banner
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Customers", f"{kpis['total_customers']:,}", help="Total number of bank account holders analyzed.")
col2.metric("Overall Churn Rate", f"{kpis['overall_churn_rate']:.1f}%", help="Percentage of total customers who left the bank.")
col3.metric("High-Value Churn Rate", f"{kpis['high_value_churn_rate']:.1f}%", help="Churn rate for customers with balance > €100k.")
col4.metric("Inactive Member Churn", f"{kpis['inactive_churn_rate']:.1f}%", help="Churn rate among inactive accounts.")
col5.metric("Capital at Risk (€)", f"€{kpis['total_churned_balance']:,.0f}", help="Total account balance lost to high-value customer churn.")

# Visual Analytics Section
tab1, tab2, tab3 = st.tabs(["🌍 Geography & Demographics", "📊 Product & Balance Analytics", "📋 Customer Data Explorer"])

with tab1:
    st.subheader("Geographic & Demographic Attrition Patterns")
    c1, c2 = st.columns(2)
    
    # 1. Geographic Churn Chart
    geo_churn = df.groupby('Geography')['Exited'].mean().reset_index()
    geo_churn['ChurnRate'] = geo_churn['Exited'] * 100
    fig_geo = px.bar(
        geo_churn, 
        x='Geography', 
        y='ChurnRate', 
        color='Geography',
        title="Churn Rate (%) by Country",
        text_auto='.1f',
        labels={'ChurnRate': 'Churn Rate (%)', 'Geography': 'Country'}
    )
    fig_geo.update_layout(showlegend=False, yaxis_title="Churn Rate (%)")
    c1.plotly_chart(fig_geo, use_container_width=True)
    
    # 2. Age & Gender Churn Chart
    age_churn = df.groupby(['AgeGroup', 'Gender'])['Exited'].mean().reset_index()
    age_churn['ChurnRate'] = age_churn['Exited'] * 100
    fig_age = px.bar(
        age_churn, 
        x='AgeGroup', 
        y='ChurnRate', 
        color='Gender', 
        barmode='group',
        text_auto='.1f',
        title="Churn Rate by Age Group & Gender (%)",
        labels={'ChurnRate': 'Churn Rate (%)', 'AgeGroup': 'Age Bracket'}
    )
    fig_age.update_layout(yaxis_title="Churn Rate (%)")
    c2.plotly_chart(fig_age, use_container_width=True)

with tab2:
    st.subheader("Financial Profile & Product Engagement Risk")
    c1, c2 = st.columns(2)
    
    # 3. Product Engagement Chart
    prod_churn = df.groupby('NumOfProducts')['Exited'].mean().reset_index()
    prod_churn['ChurnRate'] = prod_churn['Exited'] * 100
    prod_churn['NumOfProducts'] = prod_churn['NumOfProducts'].astype(str) # Treat as discrete category
    
    fig_prod = px.bar(
        prod_churn, 
        x='NumOfProducts', 
        y='ChurnRate', 
        title="Churn Rate (%) by Number of Bank Products",
        text_auto='.1f',
        labels={'ChurnRate': 'Churn Rate (%)', 'NumOfProducts': 'Number of Products'}
    )
    fig_prod.update_layout(yaxis_title="Churn Rate (%)")
    c1.plotly_chart(fig_prod, use_container_width=True)
    
    # 4. Salary vs Balance Scatter Plot
    # Convert Exited to readable labels for a clean legend
    df_scatter = df.copy()
    df_scatter['Status'] = df_scatter['Exited'].map({0: 'Retained', 1: 'Churned'})
    
    fig_scatter = px.scatter(
        df_scatter, 
        x='EstimatedSalary', 
        y='Balance', 
        color='Status',
        color_discrete_map={'Retained': '#2ecc71', 'Churned': '#e74c3c'},
        title="Salary vs. Balance Distribution",
        labels={'EstimatedSalary': 'Estimated Salary (€)', 'Balance': 'Account Balance (€)'},
        opacity=0.7
    )
    c2.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Filtered Customer-Level Drill-down")
    
    # Selected columns to display
    display_df = df[['CustomerId', 'Geography', 'Gender', 'Age', 'Balance', 'NumOfProducts', 'IsActiveMember', 'Exited']]
    
    # Interactive Data Table with Formatted Columns
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Balance": st.column_config.NumberColumn("Balance (€)", format="€%d"),
            "IsActiveMember": st.column_config.CheckboxColumn("Active Member?"),
            "Exited": st.column_config.CheckboxColumn("Churned?"),
        }
    )

    # Export Data CSV Button
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Customer Data (CSV)",
        data=csv_data,
        file_name="filtered_customer_churn_data.csv",
        mime="text/csv",
        help="Click to download the currently filtered dataset as a CSV file."
    )
