import pandas as pd
import numpy as np

def load_and_preprocess_data(filepath):
    # Read the data file (supports CSV or Excel)
    if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)
    
    # Remove non-analytical identification columns
    cols_to_drop = [c for c in ['Surname', 'Year'] if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        
    # Clean binary/integer types
    df['Exited'] = df['Exited'].astype(int)
    df['IsActiveMember'] = df['IsActiveMember'].astype(int)
    
    # 1. Age Grouping (<30, 30–45, 46–60, 60+)
    df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 29, 45, 60, 120], labels=['<30', '30–45', '46–60', '60+'])
    
    # 2. Credit Score Grouping
    df['CreditScoreBand'] = pd.cut(df['CreditScore'], bins=[0, 599, 749, 900], labels=['Low (<600)', 'Medium (600-749)', 'High (750+)'])
    
    # 3. Tenure Grouping
    df['TenureGroup'] = pd.cut(df['Tenure'], bins=[-1, 2, 7, 100], labels=['New (0-2 yrs)', 'Mid-term (3-7 yrs)', 'Long-term (8+ yrs)'])
    
    # 4. High-Value Customer Tagging (Top 25% Balance)
    bal_75th = df['Balance'].quantile(0.75)
    df['IsHighValue'] = np.where(df['Balance'] >= bal_75th, 1, 0)
    
    return df

def calculate_kpis(df):
    total = len(df)
    churned = df['Exited'].sum()
    churn_rate = (churned / total * 100) if total > 0 else 0
    
    high_val = df[df['IsHighValue'] == 1]
    high_val_churn = (high_val['Exited'].sum() / len(high_val) * 100) if len(high_val) > 0 else 0
    
    inactive = df[df['IsActiveMember'] == 0]
    inactive_churn = (inactive['Exited'].sum() / len(inactive) * 100) if len(inactive) > 0 else 0
    
    return {
        "total_customers": total,
        "overall_churn_rate": churn_rate,
        "high_value_churn_rate": high_val_churn,
        "inactive_churn_rate": inactive_churn,
        "total_churned_balance": df[df['Exited'] == 1]['Balance'].sum()
    }
