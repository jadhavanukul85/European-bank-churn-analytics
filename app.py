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
# Gen Z Modern Executive Theme (Explicit Colors - Consistent across Light & Dark OS themes)
st.markdown("""
<style>
    /* Force high contrast text colors globally across OS theme switches */
    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        color: #f3f4f6 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Main App Background: Deep Midnight Blue/Indigo Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #111827 0%, #0f0a1e 50%, #030014 100%) !important;
    }

    /* Sidebar Background and Border */
    section[data-testid="stSidebar"] {
        background-color: #0b0918 !important;
        border-right: 1px solid rgba(139, 92, 246, 0.25) !important;
    }

    /* Sidebar Headers, Labels, Subheaders & Caption Override */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] caption {
        color: #e2e8f0 !important;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: rgba(22, 19, 43, 0.85) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    /* Hover Effect on Metric Cards */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: #38bdf8 !important;
        box-shadow: 0 12px 30px rgba(56, 189, 248, 0.25) !important;
    }

    /* Top Accent Line on Metric Cards */
    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #a855f7, #38bdf8, #34d399);
    }

    /* KPI Titles / Labels inside Metric Cards */
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* KPI Metric Values Color */
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* Tab Headers */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }

    button[aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(139, 92, 246, 0.3) !important;
        border-bottom: 2px solid #a855f7 !important;
    }

    /* Buttons: Purple/Blue Gradient */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }

    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

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

# 1. Apply Filters First (Creates the 'df' variable)
df = df_raw[
    (df_raw['Geography'].isin(selected_geo)) &
    (df_raw['Gender'].isin(selected_gender)) &
    (df_raw['AgeGroup'].isin(selected_age)) &
    (df_raw['Balance'] >= min_balance)
]

# 2. Dataset Overview Sidebar Card (Placed AFTER 'df' is created)
st.sidebar.divider()
st.sidebar.markdown("### 📊 Dataset Overview")
st.sidebar.caption(f"**Total Records:** {len(df_raw):,} customers")
st.sidebar.caption(f"**Filtered Output:** {len(df):,} customers")
st.sidebar.caption("**Data Source:** European Banking Group")

# What-If Retention Simulator
st.sidebar.divider()
st.sidebar.markdown("### 💡 Retention Simulator")

target_retention = st.sidebar.slider(
    "Target Retention (%)", 
    min_value=5, 
    max_value=50, 
    value=10, 
    step=5,
    help="Simulate saving a percentage of currently churned customers."
)

churned_df = df[df['Exited'] == 1]
if len(churned_df) > 0:
    avg_balance = churned_df['Balance'].mean()
    churned_count = len(churned_df)
    saved_customers = int(churned_count * (target_retention / 100))
    saved_capital = saved_customers * avg_balance
    st.sidebar.success(f"**Saved Capital:** €{saved_capital:,.0f}\n\n({saved_customers:,} customers saved)")
else:
    st.sidebar.info("No churned customers in selected filter.")

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
