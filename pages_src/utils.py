import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("IBM_HR_Analytics_Employee_Attrition.csv")

    df['AgeGroup'] = pd.cut(df['Age'], bins=[0,25,35,45,100],
                            labels=['18-25','26-35','36-45','46+'])
    df['IncomeGroup'] = pd.cut(df['MonthlyIncome'],
                               bins=[0,3000,6000,10000,100000],
                               labels=['<$3K','$3K-6K','$6K-10K','$10K+'])
    df['TenureGroup'] = pd.cut(df['YearsAtCompany'], bins=[0,2,5,10,100],
                               labels=['0-2 yrs','3-5 yrs','6-10 yrs','10+ yrs'])
    df['AttritionBool'] = (df['Attrition'] == 'Yes').astype(int)
    df['RiskScore']    = df.apply(calculate_risk_score, axis=1)
    df['RiskCategory'] = pd.cut(df['RiskScore'], bins=[0,25,50,75,100],
                                labels=['Low','Medium','High','Critical'])
    return df


def calculate_risk_score(row):
    s = 0
    if row['Age'] < 30:                       s += 15
    elif row['Age'] < 40:                     s += 10
    elif row['Age'] > 55:                     s += 5
    if row['MonthlyIncome'] < 3000:           s += 20
    elif row['MonthlyIncome'] < 5000:         s += 10
    if row['JobSatisfaction'] == 1:           s += 20
    elif row['JobSatisfaction'] == 2:         s += 10
    if row['EnvironmentSatisfaction'] == 1:   s += 15
    elif row['EnvironmentSatisfaction'] == 2: s += 8
    if row['WorkLifeBalance'] == 1:           s += 18
    elif row['WorkLifeBalance'] == 2:         s += 9
    if row['OverTime'] == 'Yes':              s += 12
    if row['YearsSinceLastPromotion'] > 5:    s += 10
    elif row['YearsSinceLastPromotion'] > 3:  s += 5
    if row['JobInvolvement'] == 1:            s += 15
    elif row['JobInvolvement'] == 2:          s += 8
    if row['DistanceFromHome'] > 20:          s += 8
    elif row['DistanceFromHome'] > 15:        s += 4
    if row['YearsAtCompany'] < 2:             s += 12
    elif row['YearsAtCompany'] < 5:           s += 6
    if row['StockOptionLevel'] >= 2:          s -= 10
    elif row['StockOptionLevel'] == 1:        s -= 5
    if row['JobLevel'] >= 4:                  s -= 10
    elif row['JobLevel'] >= 3:                s -= 5
    return int(min(100, max(0, s)))


def score_from_inputs(age, monthly_income, job_sat, env_sat, wlb,
                      overtime, yrs_since_promo, job_involvement,
                      distance, yrs_at_company, stock_option, job_level):
    row = {
        'Age': age, 'MonthlyIncome': monthly_income,
        'JobSatisfaction': job_sat, 'EnvironmentSatisfaction': env_sat,
        'WorkLifeBalance': wlb, 'OverTime': 'Yes' if overtime else 'No',
        'YearsSinceLastPromotion': yrs_since_promo,
        'JobInvolvement': job_involvement, 'DistanceFromHome': distance,
        'YearsAtCompany': yrs_at_company, 'StockOptionLevel': stock_option,
        'JobLevel': job_level,
    }
    return calculate_risk_score(row)


def risk_color(score):
    if score < 26:  return '#10b981', 'Low'
    if score < 51:  return '#f59e0b', 'Medium'
    if score < 76:  return '#f97316', 'High'
    return '#ef4444', 'Critical'


def financial_metrics(df):
    att_count  = df['AttritionBool'].sum()
    att_rate   = att_count / len(df) * 100
    avg_annual = df['MonthlyIncome'].mean() * 12
    replacement  = att_count * avg_annual * 1.5
    productivity = att_count * 45 * (avg_annual / 260)
    training     = att_count * avg_annual * 0.10
    total        = replacement + productivity + training
    return {
        'att_count': att_count,
        'att_rate':  att_rate,
        'avg_annual': avg_annual,
        'replacement': replacement,
        'productivity': productivity,
        'training': training,
        'total': total,
    }
