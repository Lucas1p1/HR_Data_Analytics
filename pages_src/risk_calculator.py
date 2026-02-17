import streamlit as st
import plotly.graph_objects as go
from pages_src.utils import load_data, score_from_inputs, risk_color

ACCENT  = '#e84393'
SUCCESS = '#10b981'
WARNING = '#f59e0b'
DANGER  = '#ef4444'
ORANGE  = '#f97316'
BG      = '#1a1a2e'
BORDER  = '#2a2a3a'
TEXT    = '#f0f0f5'
MUTED   = '#8888aa'

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=TEXT),
    margin=dict(l=10, r=10, t=30, b=10),
)

FACTOR_WEIGHTS = {
    'Low Income (<$3K)':          20,
    'Low Job Satisfaction':        20,
    'Poor Work-Life Balance':      18,
    'Low Environment Satisfaction':15,
    'Young Age (<30)':             15,
    'Low Job Involvement':         15,
    'Short Tenure (<2 yrs)':       12,
    'Working Overtime':            12,
    'Long Since Promotion (5+ yrs)':10,
    'High Stock Options':         -10,
    'Senior Job Level (4+)':      -10,
}


def show():
    df = load_data()

    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <div class='section-header'>🎯 Interactive Risk Calculator</div>
      <div class='section-sub'>
        Enter an employee's profile to get an instant attrition risk score and personalised intervention recommendations.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── INPUTS ────────────────────────────────────────────────────────────────
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("#### Employee Profile")

        c1, c2 = st.columns(2)
        with c1:
            age = st.slider("Age", 18, 65, 28)
            monthly_income = st.slider("Monthly Income ($)", 1000, 20000, 4000, step=100)
            yrs_at_company = st.slider("Years at Company", 0, 40, 2)
            yrs_since_promo = st.slider("Years Since Last Promotion", 0, 15, 3)
        with c2:
            distance = st.slider("Distance from Home (miles)", 1, 30, 10)
            stock_option = st.select_slider("Stock Option Level", options=[0,1,2,3], value=0)
            job_level = st.select_slider("Job Level", options=[1,2,3,4,5], value=2)
            overtime = st.toggle("Working Overtime", value=False)

        st.markdown("#### Satisfaction Scores *(1 = Low, 4 = High)*")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            job_sat = st.select_slider("Job Sat.", options=[1,2,3,4], value=3)
        with s2:
            env_sat = st.select_slider("Env. Sat.", options=[1,2,3,4], value=3)
        with s3:
            wlb = st.select_slider("WLB", options=[1,2,3,4], value=3)
        with s4:
            job_inv = st.select_slider("Job Inv.", options=[1,2,3,4], value=3)

    # ── SCORE CALCULATION ─────────────────────────────────────────────────────
    score = score_from_inputs(
        age, monthly_income, job_sat, env_sat, wlb,
        overtime, yrs_since_promo, job_inv,
        distance, yrs_at_company, stock_option, job_level
    )
    color, category = risk_color(score)

    with right:
        # Score display
        st.markdown(f"""
        <div class='risk-score-display' style='background:{color}18; border-color:{color}'>
          <div class='risk-score-number' style='color:{color}'>{score}</div>
          <div style='color:{MUTED};font-size:0.8rem;margin-top:0.25rem'>out of 100</div>
          <div class='risk-score-label' style='color:{color}'>{category} Risk</div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode='gauge+number',
            value=score,
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=MUTED,
                          tickfont=dict(color=MUTED)),
                bar=dict(color=color, thickness=0.25),
                bgcolor='rgba(0,0,0,0)',
                bordercolor=BORDER,
                steps=[
                    dict(range=[0,25],   color='rgba(16,185,129,0.15)'),
                    dict(range=[25,50],  color='rgba(245,158,11,0.15)'),
                    dict(range=[50,75],  color='rgba(249,115,22,0.15)'),
                    dict(range=[75,100], color='rgba(239,68,68,0.15)'),
                ],
                threshold=dict(line=dict(color=color, width=3), value=score),
            ),
            number=dict(font=dict(color=color, size=36), suffix='/100'),
        ))
        fig_gauge.update_layout(**PLOTLY_LAYOUT, height=220)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Percentile vs dataset
        pct = (df['RiskScore'] < score).mean() * 100
        st.markdown(f"""
        <div style='background:{BG};border:1px solid {BORDER};border-radius:8px;
                    padding:0.75rem 1rem;text-align:center;margin-bottom:1rem'>
          <span style='color:{MUTED};font-size:0.8rem'>Risk percentile vs dataset</span><br/>
          <span style='font-size:1.4rem;font-weight:800;color:{color}'>{pct:.0f}th</span>
          <span style='color:{MUTED};font-size:0.85rem'> percentile</span>
        </div>
        """, unsafe_allow_html=True)

    # ── FACTOR BREAKDOWN ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### Score Breakdown — What's Driving This Risk?")

    active_factors = []
    protective_factors = []

    if age < 30:             active_factors.append(('Young Age (<30)', 15))
    elif age < 40:           active_factors.append(('Mid Age (30-40)', 10))
    if monthly_income < 3000:active_factors.append(('Low Income (<$3K)', 20))
    elif monthly_income < 5000: active_factors.append(('Below-avg Income', 10))
    if job_sat == 1:         active_factors.append(('Very Low Job Satisfaction', 20))
    elif job_sat == 2:       active_factors.append(('Low Job Satisfaction', 10))
    if env_sat == 1:         active_factors.append(('Poor Environment', 15))
    elif env_sat == 2:       active_factors.append(('Below-avg Environment', 8))
    if wlb == 1:             active_factors.append(('Poor Work-Life Balance', 18))
    elif wlb == 2:           active_factors.append(('Below-avg WLB', 9))
    if overtime:             active_factors.append(('Working Overtime', 12))
    if yrs_since_promo > 5:  active_factors.append(('5+ Yrs Since Promotion', 10))
    elif yrs_since_promo > 3:active_factors.append(('3+ Yrs Since Promotion', 5))
    if job_inv == 1:         active_factors.append(('Low Job Involvement', 15))
    elif job_inv == 2:       active_factors.append(('Below-avg Involvement', 8))
    if distance > 20:        active_factors.append(('Long Commute (>20mi)', 8))
    elif distance > 15:      active_factors.append(('Moderate Commute', 4))
    if yrs_at_company < 2:   active_factors.append(('Short Tenure (<2 yrs)', 12))
    elif yrs_at_company < 5: active_factors.append(('Early-stage Tenure', 6))
    if stock_option >= 2:    protective_factors.append(('High Stock Options', -10))
    elif stock_option == 1:  protective_factors.append(('Some Stock Options', -5))
    if job_level >= 4:       protective_factors.append(('Senior Job Level', -10))
    elif job_level >= 3:     protective_factors.append(('Mid-senior Job Level', -5))

    bc1, bc2 = st.columns(2)

    with bc1:
        if active_factors:
            labels = [f[0] for f in active_factors]
            values = [f[1] for f in active_factors]
            colors = [DANGER if v >= 15 else ORANGE if v >= 10 else WARNING for v in values]
            fig_risk = go.Figure(go.Bar(
                x=values, y=labels, orientation='h',
                marker_color=colors,
                text=[f'+{v}' for v in values],
                textposition='outside',
                textfont=dict(color=TEXT, size=11),
            ))
            fig_risk.update_layout(**PLOTLY_LAYOUT,
                title='Risk Factors (adding to score)',
                xaxis=dict(gridcolor=BORDER, range=[0, max(values)*1.4]),
                yaxis=dict(tickfont=dict(size=10)),
                height=max(200, len(active_factors)*40 + 60),
                showlegend=False,
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.success("✅ No significant risk factors detected.")

    with bc2:
        if protective_factors:
            labels = [f[0] for f in protective_factors]
            values = [abs(f[1]) for f in protective_factors]
            fig_prot = go.Figure(go.Bar(
                x=values, y=labels, orientation='h',
                marker_color=SUCCESS,
                text=[f'-{v}' for v in values],
                textposition='outside',
                textfont=dict(color=TEXT, size=11),
            ))
            fig_prot.update_layout(**PLOTLY_LAYOUT,
                title='Protective Factors (reducing score)',
                xaxis=dict(gridcolor=BORDER, range=[0, max(values)*1.4]),
                yaxis=dict(tickfont=dict(size=10)),
                height=max(200, len(protective_factors)*40 + 60),
                showlegend=False,
            )
            st.plotly_chart(fig_prot, use_container_width=True)
        else:
            st.info("ℹ️ No protective factors currently active.")

    # ── RECOMMENDATIONS ───────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 💡 Recommended Interventions")

    recs = []
    if monthly_income < 5000:
        potential_savings = monthly_income * 12 * 1.5
        increase = monthly_income * 0.10 * 12
        recs.append(("💰 Compensation Review",
                     f"A 10% salary increase costs <b>${increase:,.0f}/year</b> but avoids <b>${potential_savings:,.0f}</b> in replacement costs — a {potential_savings/increase:.0f}× return."))
    if overtime:
        recs.append(("⏰ Overtime Reduction",
                     "Overtime employees leave at 2× the rate. Review workload distribution or hire additional headcount to reduce dependency."))
    if job_sat <= 2 or env_sat <= 2:
        recs.append(("😊 Satisfaction Improvement",
                     "Low satisfaction scores are among the strongest predictors. Schedule a 1-on-1 to identify specific pain points — team dynamics, role clarity, or growth opportunities."))
    if yrs_since_promo > 3:
        recs.append(("📈 Career Development",
                     f"{yrs_since_promo} years without promotion is a strong flight risk signal. Discuss a concrete promotion timeline or expand scope of current role."))
    if wlb <= 2:
        recs.append(("⚖️ Work-Life Balance",
                     "Consider flexible hours, remote work options, or reduced project load. WLB score of 1-2 is correlated with some of the highest attrition rates in the dataset."))
    if yrs_at_company < 2:
        recs.append(("🎓 Onboarding & Mentorship",
                     "Early tenure is the highest-risk period. Assign a dedicated mentor and ensure 30/60/90 day check-ins are happening consistently."))
    if not recs:
        recs.append(("✅ Low Immediate Risk",
                     "No critical interventions needed. Maintain regular check-ins and continue monitoring satisfaction scores."))

    for title, body in recs:
        st.markdown(f"""
        <div class='finding-box'>
          <b>{title}</b><br/>{body}
        </div>
        """, unsafe_allow_html=True)
