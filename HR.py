import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import datetime as dt

st.set_page_config(layout='wide', page_title='HR Analysis')

# Load Data
df = pd.read_csv("HRDataset.csv")
date_columns = ['DOB', 'DateofTermination', 'LastPerformanceReview_Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col])
df['DateofHire'] = pd.to_datetime(df['DateofHire'])
df['year_of_Hire'] = df['DateofHire'].dt.year

# Sidebar Filters
st.sidebar.header("Filter Options")
year_options = ['All'] + sorted(df['year_of_Hire'].dropna().unique().tolist())
status_options = ['All'] + sorted(df['EmploymentStatus'].dropna().unique().tolist())
source_options = ['All'] + sorted(df['RecruitmentSource'].dropna().unique().tolist())

selected_year_of_Hire = st.sidebar.selectbox("Select year_of_Hire:", options=year_options)
selected_EmploymentStatus = st.sidebar.selectbox("Select EmploymentStatus:", options=status_options)
selected_RecruitmentSource = st.sidebar.selectbox("Select RecruitmentSource:", options=source_options)

# Apply filters
if selected_year_of_Hire != 'All':
    df = df[df['year_of_Hire'] == selected_year_of_Hire]
if selected_EmploymentStatus != 'All':
    df = df[df['EmploymentStatus'] == selected_EmploymentStatus]
if selected_RecruitmentSource != 'All':
    df = df[df['RecruitmentSource'] == selected_RecruitmentSource]

# Drop unnecessary columns
df.drop(columns=['MarriedID', 'MaritalStatusID', 'GenderID','EmpStatusID', 'DeptID', 'PerfScoreID', 'FromDiversityJobFairID','PositionID','ManagerID','Termd'], inplace=True)

# Summary Metrics
total_employees = df['Employee_Name'].nunique()
total_races = df['RaceDesc'].nunique()
total_females = df[df['Sex'] == 'Female']['Employee_Name'].nunique()
total_absences = df['Absences'].sum()
Total_Salary = str(round(df['Salary'].sum() / 1_000_000, 2)) + 'M'
Average_Salary = str(round(df['Salary'].mean() / 1_000, 2)) + 'K'
df['Age'] = dt.datetime.now().year - df['DOB'].dt.year
Average_Age = df['Age'].mean()

# Metric Card Template
def bordered_metric(label, value):
    st.markdown(f"""
    <div style="border:1px solid #ccc; border-radius:16px; text-align:center; background-color:#f9f9f9; padding:8px; font-size:15px">
        <div style="margin-bottom:2px">{label}</div>
        <div style="font-size:24px; color:#0E1117; font-weight:bold">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# First Row Metrics
col1, col2, col3 = st.columns(3)
with col1:
    bordered_metric("👥 Total Employees", total_employees)
with col2:
    bordered_metric("🌍 Races", total_races)
with col3:
    bordered_metric("🏥 Total Absences", int(total_absences))

st.write("")

# Second Row Metrics
col1, col2, col3 = st.columns(3)
with col1:
    bordered_metric("💰 Total Salary", Total_Salary)
with col2:
    bordered_metric("💵 Average Salary", Average_Salary)
with col3:
    bordered_metric("🎂 Average Age", round(Average_Age))

# Visualizations
col1, col2 = st.columns(2)
with col1:
    sex_dist = df.groupby('Sex')['Employee_Name'].count().reset_index(name='Employee_count')
    fig1 = px.pie(sex_dist, names='Sex', values='Employee_count', color_discrete_sequence=['#c90076', '#2986cc'])
    st.subheader('Number of Employees per Sex')
    st.plotly_chart(fig1)
with col2:
    race_dist = df.groupby('RaceDesc')['Employee_Name'].count().sort_values(ascending=False).reset_index()
    fig2 = px.bar(race_dist, x='RaceDesc', y='Employee_Name', text='Employee_Name', color_discrete_sequence=['#27548A'])
    fig2.update_traces(textposition='outside', textfont=dict(size=8))
    fig2.update_layout(yaxis=dict(showgrid=False), xaxis=dict(tickangle=30, tickfont=dict(size=10)))
    st.subheader('Number of Employees per Race')
    st.plotly_chart(fig2)

col1, col2 = st.columns(2)
with col1:
    citizenship = df.groupby('CitizenDesc')['Employee_Name'].count().reset_index(name='Employee_count')
    fig3 = px.pie(citizenship, names='CitizenDesc', values='Employee_count', color_discrete_sequence=['#A89CF8', '#A3B7F5', '#527AF2'])
    st.subheader('Percentage of Employees per Citizenship')
    st.plotly_chart(fig3)
with col2:
    salary_sex = df.groupby('Sex')['Salary'].sum().reset_index(name='Sum_Salary')
    salary_sex['Sum_Salary_M'] = (salary_sex['Sum_Salary'] / 1_000_000).round(2).astype(str) + 'M'
    fig4 = px.pie(salary_sex, names='Sex', values='Sum_Salary', color_discrete_sequence=['#c90076', '#2986cc'])
    fig4.update_traces(text=salary_sex['Sum_Salary_M'], textinfo='label+text')
    st.subheader('Sum of Salaries per Sex')
    st.plotly_chart(fig4)

state_count = df.groupby('State')['Employee_Name'].count().reset_index(name='Employee_Count')
fig5 = px.choropleth(state_count, locations='State', locationmode='USA-states', color='Employee_Count', color_continuous_scale='reds', scope='usa')
st.header('Number of Employees per U.S. State')
st.plotly_chart(fig5)

hire_trend = df.groupby(['year_of_Hire', 'Sex'])['Employee_Name'].count().reset_index(name='hired_employees')
fig6 = px.line(hire_trend, x='year_of_Hire', y='hired_employees', color='Sex', color_discrete_sequence=['#c90076', '#2986cc'], markers=True, text='hired_employees')
fig6.update_traces(textposition='top center', textfont_size=8)
fig6.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
st.subheader('Number of Employees Hired per Year')
st.plotly_chart(fig6)

col1, col2 = st.columns(2)
with col1:
    avg_salary = df.groupby(['EmpSatisfaction', 'CitizenDesc'])['Salary'].mean().reset_index(name='Avg_Salary')
    avg_salary['Avg_Salary_K'] = (avg_salary['Avg_Salary'] / 1000).round(1).astype(str) + 'K'
    fig7 = px.line(avg_salary, x='EmpSatisfaction', y='Avg_Salary', color='CitizenDesc', markers=True, text='Avg_Salary_K', color_discrete_sequence=['#A89CF8', '#F28907', '#527AF2'])
    fig7.update_traces(textposition='top center', textfont_size=10)
    fig7.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.subheader('Average Salary by Employee Satisfaction')
    st.plotly_chart(fig7)

with col2:
    conditions = [
        (df['Salary'] >=30000) & (df['Salary']<40000),
        (df['Salary'] >=40000) & (df['Salary']<50000),
        (df['Salary'] >=50000) & (df['Salary']<60000),
        (df['Salary'] >=60000) & (df['Salary']<70000),
        (df['Salary'] >=70000) 
    ]
    choices = ['30-40K', '40-50K', '50-60K', '60-70K', '+70K']
    
    df['Range'] = np.select(conditions, choices, default='Unknown')
    num_of_Employee_by_rangeOfSalaries = df.groupby(['Range'])['Employee_Name'].count().reset_index(name='num_of_Employee')
    fig07=px.funnel_area(num_of_Employee_by_rangeOfSalaries,names='Range',values='num_of_Employee', color_discrete_sequence = ['#335CB8','#5478C7','#7B9AE1','#99B7F9'])
    st.subheader('number of Employees by range Of Salaries')
    st.plotly_chart(fig07)
