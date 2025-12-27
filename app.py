# smit_executive_dashboard.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="SMIT Executive Dashboard",
    page_icon="🎓",
    layout="wide"
)

# --- Dark Mode Header ---
st.markdown("""
<div style="background-color:#0A0A23;padding:20px;border-radius:12px;margin-bottom:20px">
<h1 style="color:#00BFFF;text-align:center;">🎓 SMIT Academy Executive Dashboard</h1>
<p style="color:#B0C4DE;text-align:center;">Advanced Analytics & Student Performance Overview</p>
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
DATA_FILE = "StudentsPerformance.csv"
if not os.path.exists(DATA_FILE):
    st.warning("CSV not found! Generating sample dataset...")
    np.random.seed(42)
    df = pd.DataFrame({
        'gender': np.random.choice(['male','female'], 100),
        'parental level of education': np.random.choice(['high school','associate degree','bachelor','master'], 100),
        'lunch': np.random.choice(['standard','free/reduced'], 100),
        'test preparation course': np.random.choice(['none','completed'], 100),
        'math score': np.random.randint(0,101,100),
        'reading score': np.random.randint(0,101,100),
        'writing score': np.random.randint(0,101,100)
    })
else:
    df = pd.read_csv(DATA_FILE)

# --- Data Prep ---
FAIL_THRESHOLD = 40
df['total score'] = df[['math score','reading score','writing score']].sum(axis=1)
df['average score'] = df['total score']/3
df['min score'] = df[['math score','reading score','writing score']].min(axis=1)
df['pass_fail'] = df['min score'].apply(lambda x: 'Fail' if x <= FAIL_THRESHOLD else 'Pass')

# --- Sidebar Filters ---
st.sidebar.header("Filter Students")
gender_filter = st.sidebar.multiselect("Gender", df['gender'].unique(), df['gender'].unique())
edu_filter = st.sidebar.multiselect("Parental Education", df['parental level of education'].unique(), df['parental level of education'].unique())
prep_filter = st.sidebar.multiselect("Test Prep Course", df['test preparation course'].unique(), df['test preparation course'].unique())

filtered_df = df[
    (df['gender'].isin(gender_filter)) &
    (df['parental level of education'].isin(edu_filter)) &
    (df['test preparation course'].isin(prep_filter))
]

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🏠 Overview", "📊 Trends & Visuals", "⚠️ At-Risk Students"])

# --- Tab 1: Overview ---
with tab1:
    st.header("🏠 Overview")

    pass_count = filtered_df['pass_fail'].value_counts().get('Pass',0)
    fail_count = filtered_df['pass_fail'].value_counts().get('Fail',0)
    total_students = len(filtered_df)
    pass_percent = pass_count/total_students*100 if total_students>0 else 0
    fail_percent = fail_count/total_students*100 if total_students>0 else 0

    # Neon-style KPI cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.markdown(f"""
    <div style="background-color:#001f3f;padding:20px;border-radius:12px;text-align:center;">
    <h3 style="color:#00ffff">Total Students</h3>
    <h1 style="color:#00ffff">{total_students}</h1>
    </div>
    """, unsafe_allow_html=True)
    kpi2.markdown(f"""
    <div style="background-color:#003366;padding:20px;border-radius:12px;text-align:center;">
    <h3 style="color:#00ff7f">Pass %</h3>
    <h1 style="color:#00ff7f">{pass_percent:.2f}%</h1>
    </div>
    """, unsafe_allow_html=True)
    kpi3.markdown(f"""
    <div style="background-color:#330000;padding:20px;border-radius:12px;text-align:center;">
    <h3 style="color:#ff4d4d">Fail %</h3>
    <h1 style="color:#ff4d4d">{fail_percent:.2f}%</h1>
    </div>
    """, unsafe_allow_html=True)

    # Average Scores Table
    avg_scores = filtered_df[['math score','reading score','writing score']].mean()
    avg_scores_df = pd.DataFrame(avg_scores).reset_index()
    avg_scores_df.columns = ['Subject','Average Score']
    st.markdown("### Average Scores by Subject")
    st.table(avg_scores_df.style.set_properties(**{'background-color': '#001f3f', 'color': 'white', 'border-color': 'white'}))

    # Pass/Fail Pie Chart
    st.markdown("### Pass vs Fail Distribution")
    fig = px.pie(filtered_df, names='pass_fail', color='pass_fail',
                 color_discrete_map={'Pass':'#00ff7f','Fail':'#ff4d4d'},
                 title="Pass vs Fail")
    fig.update_layout(plot_bgcolor='#0A0A23', paper_bgcolor='#0A0A23', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Trends & Visuals ---
with tab2:
    st.header("📊 Performance Trends")

    # Scatter Plot
    st.markdown("### Scatter Plot: Math vs Reading")
    fig = px.scatter(filtered_df, x='math score', y='reading score', color='pass_fail',
                     hover_data=['gender','parental level of education','test preparation course'],
                     color_discrete_map={'Pass':'#00ff7f','Fail':'#ff4d4d'},
                     title="Math vs Reading Scores")
    fig.add_hline(y=FAIL_THRESHOLD, line_dash="dot", line_color="#ff4d4d")
    fig.add_vline(x=FAIL_THRESHOLD, line_dash="dot", line_color="#ff4d4d")
    fig.update_layout(plot_bgcolor='#0A0A23', paper_bgcolor='#0A0A23', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.markdown("### Heatmap: Average Scores by Gender")
    heatmap_df = filtered_df.groupby('gender')[['math score','reading score','writing score']].mean().round(2)
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale='Viridis',
        colorbar_title="Avg Score"
    ))
    fig.update_layout(plot_bgcolor='#0A0A23', paper_bgcolor='#0A0A23', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

    # Bar Chart
    st.markdown("### Bar Chart: Average Scores by Parental Education")
    bar_df = filtered_df.groupby('parental level of education')[['math score','reading score','writing score']].mean().reset_index()
    fig = px.bar(bar_df, x='parental level of education', y=['math score','reading score','writing score'],
                 barmode='group', color_discrete_sequence=['#00BFFF','#00ff7f','#ff4d4d'],
                 labels={'value':'Average Score','parental level of education':'Parental Education','variable':'Subject'},
                 title="Average Scores by Parental Education")
    fig.update_layout(plot_bgcolor='#0A0A23', paper_bgcolor='#0A0A23', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: At-Risk Students ---
with tab3:
    st.header("⚠️ At-Risk Students")
    at_risk = filtered_df[filtered_df['pass_fail']=='Fail'].sort_values(by='min score')
    st.dataframe(at_risk[['gender','parental level of education','lunch','test preparation course','math score','reading score','writing score','min score']])

    csv = at_risk.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download At-Risk Report", csv, "smit_at_risk_report.csv","text/csv")

# --- Footer with Developer ---
st.markdown("---")
st.markdown("<div style='text-align:center;color:#B0C4DE;'>© 2025 SMIT Academy | Developed by <b>MUHAMMAD AZHAR</b> | Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
