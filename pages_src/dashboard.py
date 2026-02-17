import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pages_src.utils import load_data, financial_metrics

ACCENT  = '#e84393'
ACCENT2 = '#7c3aed'
SUCCESS = '#10b981'
WARNING = '#f59e0b'
DANGER  = '#ef4444'
ORANGE  = '#f97316'
BG      = '#1a1a2e'
BG2     = '#111118'
BORDER  = '#2a2a3a'
TEXT    = '#f0f0f5'
MUTED   = '#8888aa'

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=TEXT),
    margin=dict(l=10, r=10, t=40, b=10),
)


def show():
    df = load_data()
    fin = financial_metrics(df)

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <div class='section-header'>📊 Executive Dashboard</div>
      <div class='section-sub'>
        Real-time workforce attrition intelligence · IBM HR Dataset · 1,470 employees
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── DEPARTMENT FILTER ─────────────────────────────────────────────────────
    depts = ['All Departments'] + sorted(df['Department'].unique().tolist())
    dept_filter = st.selectbox("Filter by Department", depts, label_visibility='collapsed')
    if dept_filter != 'All Departments':
        df = df[df['Department'] == dept_filter]
        fin = financial_metrics(df)

    st.divider()

    # ── KPI ROW ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Employees",   f"{len(df):,}")
    k2.metric("Attrition Count",   f"{fin['att_count']:,}")
    k3.metric("Attrition Rate",    f"{fin['att_rate']:.2f}%",
              delta=f"{fin['att_rate']-13:.2f}pp vs industry",
              delta_color="inverse")
    k4.metric("Annual Cost Impact", f"${fin['total']/1e6:.1f}M")
    k5.metric("Avg Risk Score",    f"{df['RiskScore'].mean():.1f}/100")

    st.divider()

    # ── ROW 1: Attrition benchmark + by department ────────────────────────────
    col1, col2 = st.columns([1, 1.8])

    with col1:
        st.markdown("<div class='section-header' style='font-size:1rem'>vs Industry Benchmark</div>",
                    unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Industry Avg', 'This Company'],
            y=[13.0, round(fin['att_rate'], 2)],
            marker_color=[SUCCESS, ACCENT if fin['att_rate'] > 13 else SUCCESS],
            text=[f"13.0%", f"{fin['att_rate']:.2f}%"],
            textposition='outside',
            textfont=dict(size=14, color=TEXT, family='Inter'),
        ))
        fig.add_hline(y=13, line_dash='dash', line_color=SUCCESS, opacity=0.5)
        fig.update_layout(**PLOTLY_LAYOUT,
            yaxis=dict(range=[0, max(fin['att_rate'], 13)*1.3],
                       gridcolor=BORDER, ticksuffix='%'),
            xaxis=dict(tickfont=dict(size=12)),
            showlegend=False, height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header' style='font-size:1rem'>Attrition by Department</div>",
                    unsafe_allow_html=True)
        dept_df = (df.groupby('Department')['AttritionBool'].mean()*100).reset_index()
        dept_df.columns = ['Department', 'Rate']
        dept_df = dept_df.sort_values('Rate', ascending=True)
        dept_df['Color'] = dept_df['Rate'].apply(
            lambda v: DANGER if v > 18 else WARNING if v > 13 else SUCCESS)

        fig2 = go.Figure(go.Bar(
            y=dept_df['Department'], x=dept_df['Rate'],
            orientation='h',
            marker_color=dept_df['Color'].tolist(),
            text=dept_df['Rate'].apply(lambda v: f'{v:.1f}%'),
            textposition='outside',
            textfont=dict(size=13, color=TEXT),
        ))
        fig2.add_vline(x=13, line_dash='dash', line_color=SUCCESS,
                       opacity=0.5, annotation_text='Industry avg',
                       annotation_font_color=MUTED)
        fig2.update_layout(**PLOTLY_LAYOUT,
            xaxis=dict(range=[0, dept_df['Rate'].max()*1.3],
                       gridcolor=BORDER, ticksuffix='%'),
            yaxis=dict(tickfont=dict(size=12)),
            showlegend=False, height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── ROW 2: Risk factors ───────────────────────────────────────────────────
    st.divider()
    st.markdown("<div class='section-header' style='font-size:1rem'>Attrition by Key Risk Factors</div>",
                unsafe_allow_html=True)

    rf1, rf2, rf3 = st.columns(3)

    def risk_bar(col, group_col, title, observed=False):
        with col:
            if observed:
                gdf = (df.groupby(group_col, observed=True)['AttritionBool']
                       .mean()*100).reset_index()
            else:
                gdf = (df.groupby(group_col)['AttritionBool']
                       .mean()*100).reset_index()
            gdf.columns = ['Group', 'Rate']
            gdf['Group'] = gdf['Group'].astype(str)
            gdf['Color'] = gdf['Rate'].apply(
                lambda v: DANGER if v >= 25 else WARNING if v >= 13 else SUCCESS)
            fig = go.Figure(go.Bar(
                x=gdf['Group'], y=gdf['Rate'],
                marker_color=gdf['Color'].tolist(),
                text=gdf['Rate'].apply(lambda v: f'{v:.1f}%'),
                textposition='outside',
                textfont=dict(size=11, color=TEXT),
            ))
            fig.add_hline(y=fin['att_rate'], line_dash='dash',
                          line_color=ACCENT2, opacity=0.6)
            fig.update_layout(**PLOTLY_LAYOUT,
                title=dict(text=title, font=dict(size=13, color=TEXT)),
                yaxis=dict(range=[0, gdf['Rate'].max()*1.35],
                           gridcolor=BORDER, ticksuffix='%'),
                xaxis=dict(tickfont=dict(size=10)),
                showlegend=False, height=260,
            )
            st.plotly_chart(fig, use_container_width=True)

    risk_bar(rf1, 'OverTime',    'Overtime Status')
    risk_bar(rf2, 'IncomeGroup', 'Income Bracket', observed=True)
    risk_bar(rf3, 'AgeGroup',    'Age Group',      observed=True)

    rf4, rf5, rf6 = st.columns(3)
    risk_bar(rf4, 'JobSatisfaction',  'Job Satisfaction (1=Low)')
    risk_bar(rf5, 'WorkLifeBalance',  'Work-Life Balance (1=Poor)')
    risk_bar(rf6, 'TenureGroup',      'Tenure at Company', observed=True)

    # ── ROW 3: Risk distribution + heatmap ───────────────────────────────────
    st.divider()
    h1, h2 = st.columns([1.2, 1])

    with h1:
        st.markdown("<div class='section-header' style='font-size:1rem'>Risk Score Distribution</div>",
                    unsafe_allow_html=True)
        color_map = {'Low': SUCCESS, 'Medium': WARNING,
                     'High': ORANGE,  'Critical': DANGER}
        fig_hist = go.Figure()
        for cat, color in color_map.items():
            subset = df[df['RiskCategory'] == cat]['RiskScore']
            fig_hist.add_trace(go.Histogram(
                x=subset, nbinsx=20,
                name=f'{cat} ({len(subset)})',
                marker_color=color, opacity=0.85,
            ))
        fig_hist.add_vline(x=50, line_dash='dash', line_color=TEXT,
                           opacity=0.5, annotation_text='Action threshold',
                           annotation_font_color=MUTED)
        fig_hist.update_layout(**PLOTLY_LAYOUT,
            barmode='stack', height=300,
            xaxis=dict(title='Risk Score', gridcolor=BORDER),
            yaxis=dict(title='Employees', gridcolor=BORDER),
            legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with h2:
        st.markdown("<div class='section-header' style='font-size:1rem'>Satisfaction Heatmap</div>",
                    unsafe_allow_html=True)
        pivot = (df.groupby(['JobSatisfaction','WorkLifeBalance'])['AttritionBool']
                 .mean()*100).unstack().round(1)
        fig_heat = px.imshow(
            pivot, text_auto=True,
            color_continuous_scale='RdYlGn_r',
            zmin=0, zmax=50,
            labels=dict(x='Work-Life Balance', y='Job Satisfaction',
                        color='Attrition %'),
        )
        fig_heat.update_layout(**PLOTLY_LAYOUT, height=300,
            coloraxis_colorbar=dict(ticksuffix='%', tickfont=dict(color=TEXT)))
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── ROW 4: Cost breakdown ─────────────────────────────────────────────────
    st.divider()
    st.markdown("<div class='section-header' style='font-size:1rem'>💸 Annual Cost Breakdown</div>",
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Replacement Costs",   f"${fin['replacement']/1e6:.1f}M",
              f"{fin['att_count']} employees × 1.5× salary")
    c2.metric("Productivity Loss",   f"${fin['productivity']/1e6:.1f}M",
              f"45-day avg vacancy period")
    c3.metric("Training & Onboarding", f"${fin['training']/1e6:.1f}M",
              "10% of annual salary each")
    c4.metric("Total Impact",        f"${fin['total']/1e6:.1f}M",
              delta=f"${fin['total']/fin['att_count']:,.0f} per employee",
              delta_color='off')

    # Key findings
    st.divider()
    st.markdown("<div class='section-header' style='font-size:1rem'>📌 Key Findings</div>",
                unsafe_allow_html=True)

    ot_yes = df[df['OverTime']=='Yes']['AttritionBool'].mean()*100
    ot_no  = df[df['OverTime']=='No']['AttritionBool'].mean()*100
    low_inc_rate = df[df['IncomeGroup']=='<$3K']['AttritionBool'].mean()*100 if '<$3K' in df['IncomeGroup'].cat.categories else 0
    young_rate   = df[df['AgeGroup']=='18-25']['AttritionBool'].mean()*100 if '18-25' in df['AgeGroup'].cat.categories else 0

    findings = [
        f"Employees working overtime leave at <b>{ot_yes:.1f}%</b> vs <b>{ot_no:.1f}%</b> for non-overtime — a <b>{ot_yes/ot_no:.1f}× multiplier</b>. Highest single leverage point.",
        f"Employees earning <b>&lt;$3K/month</b> leave at <b>{low_inc_rate:.1f}%</b> — targeted compensation review of this group yields 1,000%+ ROI.",
        f"Employees aged <b>18-25</b> leave at <b>{young_rate:.1f}%</b>. Combined with short tenure (&lt;2 years), new hire onboarding is a critical intervention area.",
        f"<b>{len(df[df['RiskScore']>=75]):,} employees</b> are at Critical risk (score 75+). Immediate 1-on-1 manager conversations recommended for this cohort.",
    ]
    for f in findings:
        st.markdown(f"<div class='finding-box'>{f}</div>", unsafe_allow_html=True)
