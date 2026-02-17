import streamlit as st
import plotly.graph_objects as go
from pages_src.utils import load_data, financial_metrics

ACCENT  = '#e84393'
ACCENT2 = '#7c3aed'
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
    margin=dict(l=10, r=10, t=40, b=10),
)


def show():
    df = load_data()
    fin = financial_metrics(df)

    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <div class='section-header'>💰 ROI Scenario Modeler</div>
      <div class='section-sub'>
        Model the financial return of specific retention programs. Adjust the sliders to see real-time ROI projections.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── BASELINE ──────────────────────────────────────────────────────────────
    st.markdown("#### Baseline — Current State")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Total Attrition Cost",  f"${fin['total']/1e6:.1f}M")
    b2.metric("Employees at Risk",     f"{len(df[df['RiskScore']>=50]):,}")
    b3.metric("Attrition Rate",        f"{fin['att_rate']:.2f}%")
    b4.metric("Cost Per Departure",    f"${fin['total']/fin['att_count']:,.0f}")

    st.divider()

    # ── SCENARIO TABS ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Compensation Review",
        "📈 Career Development",
        "⚖️ Work-Life Balance",
        "🎯 Custom Program",
    ])

    # ── TAB 1: Compensation ───────────────────────────────────────────────────
    with tab1:
        st.markdown("##### Target: High-risk employees earning below market rate")
        c1, c2 = st.columns([1, 1])

        with c1:
            income_threshold = st.slider(
                "Target employees earning less than ($/month)",
                1000, 10000, 5000, step=500,
                help="Employees below this income AND with high risk score will be targeted"
            )
            salary_increase_pct = st.slider("Salary increase (%)", 5, 30, 10)
            expected_retention  = st.slider("Expected retention improvement (%)", 10, 80, 50,
                                            help="What % of targeted employees do you expect to retain?")

            # Calculations
            target = df[(df['MonthlyIncome'] < income_threshold) & (df['RiskScore'] >= 50)]
            n_target = len(target)
            program_cost = target['MonthlyIncome'].sum() * 12 * (salary_increase_pct/100)
            employees_retained = int(n_target * (expected_retention/100))
            avg_replacement = fin['total'] / fin['att_count']
            savings = employees_retained * avg_replacement * 0.3  # conservative 30% would have left
            roi = ((savings - program_cost) / program_cost * 100) if program_cost > 0 else 0

        with c2:
            _render_roi_result(n_target, program_cost, savings, roi,
                               employees_retained, "salary increases")

    # ── TAB 2: Career Development ─────────────────────────────────────────────
    with tab2:
        st.markdown("##### Target: High-risk employees stagnant in their career path")
        c1, c2 = st.columns([1, 1])

        with c1:
            promo_threshold = st.slider("Target employees who haven't been promoted in (years)",
                                        1, 10, 3)
            program_cost_pp = st.slider("Program cost per employee ($/year)", 500, 5000, 1500, step=100)
            expected_retention = st.slider("Expected retention improvement (%)", 10, 80, 40)

            target = df[(df['YearsSinceLastPromotion'] >= promo_threshold) &
                        (df['RiskScore'] >= 50)]
            n_target = len(target)
            program_cost = n_target * program_cost_pp
            avg_replacement = fin['total'] / fin['att_count']
            employees_retained = int(n_target * (expected_retention/100))
            savings = employees_retained * avg_replacement * 0.3
            roi = ((savings - program_cost) / program_cost * 100) if program_cost > 0 else 0

        with c2:
            _render_roi_result(n_target, program_cost, savings, roi,
                               employees_retained, "career development plans")

    # ── TAB 3: Work-Life Balance ──────────────────────────────────────────────
    with tab3:
        st.markdown("##### Target: High-risk employees with poor work-life balance scores")
        c1, c2 = st.columns([1, 1])

        with c1:
            wlb_threshold = st.select_slider("Target employees with WLB score at or below",
                                             options=[1,2,3], value=2)
            program_cost_pp = st.slider("Program cost per employee ($/year)",
                                        200, 3000, 800, step=100)
            expected_retention = st.slider("Expected retention improvement (%)", 10, 70, 35)

            target = df[(df['WorkLifeBalance'] <= wlb_threshold) &
                        (df['RiskScore'] >= 50)]
            n_target = len(target)
            program_cost = n_target * program_cost_pp
            avg_replacement = fin['total'] / fin['att_count']
            employees_retained = int(n_target * (expected_retention/100))
            savings = employees_retained * avg_replacement * 0.3
            roi = ((savings - program_cost) / program_cost * 100) if program_cost > 0 else 0

        with c2:
            _render_roi_result(n_target, program_cost, savings, roi,
                               employees_retained, "flexibility/WLB initiatives")

    # ── TAB 4: Custom ─────────────────────────────────────────────────────────
    with tab4:
        st.markdown("##### Build your own retention program scenario")
        c1, c2 = st.columns([1, 1])

        with c1:
            n_target      = st.slider("Number of employees to target", 10, 500, 100)
            program_cost  = st.slider("Total program cost ($)", 50_000, 5_000_000, 500_000, step=50_000)
            att_reduction = st.slider("Expected attrition rate reduction (pp)", 1, 10, 3,
                                      help="Percentage point reduction you expect to achieve")

            current_att_cost  = fin['total']
            projected_savings = current_att_cost * (att_reduction / fin['att_rate'])
            roi = ((projected_savings - program_cost) / program_cost * 100) if program_cost > 0 else 0
            employees_retained = int(fin['att_count'] * (att_reduction / fin['att_rate']))
            savings = projected_savings

        with c2:
            _render_roi_result(n_target, program_cost, savings, roi,
                               employees_retained, "targeted interventions")

    # ── COMBINED SCENARIO ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📊 Portfolio View — Combined Program Impact")

    programs = ['Compensation\nReview', 'Career\nDevelopment',
                'Work-Life\nBalance', 'New Hire\nOnboarding']
    inv      = [1.15, 0.50, 0.30, 0.20]
    sav      = [12.7,  8.2,  9.5,  2.4]
    rois_all = [(s-c)/c*100 for c,s in zip(inv,sav)]

    pc1, pc2 = st.columns(2)

    with pc1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Investment ($M)', x=programs, y=inv,
            marker_color=ACCENT, text=[f'${v:.2f}M' for v in inv],
            textposition='outside', textfont=dict(size=11, color=TEXT),
        ))
        fig.add_trace(go.Bar(
            name='Potential Savings ($M)', x=programs, y=sav,
            marker_color=SUCCESS, text=[f'${v:.1f}M' for v in sav],
            textposition='outside', textfont=dict(size=11, color=TEXT),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, barmode='group', height=320,
            yaxis=dict(gridcolor=BORDER, tickprefix='$', ticksuffix='M'),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with pc2:
        roi_colors = [SUCCESS if r > 500 else WARNING for r in rois_all]
        fig2 = go.Figure(go.Bar(
            x=programs, y=rois_all,
            marker_color=roi_colors,
            text=[f'{r:,.0f}%' for r in rois_all],
            textposition='outside',
            textfont=dict(size=12, color=TEXT, family='Inter'),
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=320,
            title='ROI by Program',
            yaxis=dict(gridcolor=BORDER, ticksuffix='%',
                       title='Return on Investment'),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Summary row
    total_inv = sum(inv)
    total_sav = sum(sav)
    total_roi = (total_sav - total_inv) / total_inv * 100

    s1, s2, s3 = st.columns(3)
    s1.metric("Total Portfolio Investment", f"${total_inv:.2f}M")
    s2.metric("Total Potential Savings",    f"${total_sav:.1f}M")
    s3.metric("Blended Portfolio ROI",      f"{total_roi:,.0f}%",
              delta="vs $0 investment (status quo)")


def _render_roi_result(n_target, program_cost, savings, roi, employees_retained, action_label):
    color = SUCCESS if roi > 200 else WARNING if roi > 0 else DANGER

    st.markdown(f"""
    <div style='background:{BG};border:1px solid {BORDER};border-radius:12px;
                padding:1.5rem;margin-bottom:1rem'>
      <div style='color:{MUTED};font-size:0.75rem;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:0.5rem'>Employees Targeted</div>
      <div style='font-size:2rem;font-weight:800;color:{TEXT}'>{n_target:,}</div>
    </div>
    <div style='background:{BG};border:1px solid {BORDER};border-radius:12px;
                padding:1.5rem;margin-bottom:1rem'>
      <div style='color:{MUTED};font-size:0.75rem;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:0.5rem'>Program Cost</div>
      <div style='font-size:2rem;font-weight:800;color:{DANGER}'>${program_cost:,.0f}</div>
    </div>
    <div style='background:{BG};border:1px solid {BORDER};border-radius:12px;
                padding:1.5rem;margin-bottom:1rem'>
      <div style='color:{MUTED};font-size:0.75rem;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:0.5rem'>Projected Savings</div>
      <div style='font-size:2rem;font-weight:800;color:{SUCCESS}'>${savings:,.0f}</div>
      <div style='color:{MUTED};font-size:0.8rem;margin-top:0.25rem'>
        {employees_retained} employees retained via {action_label}
      </div>
    </div>
    <div style='background:{color}18;border:2px solid {color};border-radius:12px;
                padding:1.5rem;text-align:center'>
      <div style='color:{MUTED};font-size:0.75rem;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:0.25rem'>Projected ROI</div>
      <div style='font-size:3rem;font-weight:900;color:{color};letter-spacing:-0.03em'>
        {roi:,.0f}%
      </div>
      <div style='color:{MUTED};font-size:0.8rem;margin-top:0.25rem'>
        {'✅ ROI-positive investment' if roi > 0 else '⚠️ Review program scope'}
      </div>
    </div>
    """, unsafe_allow_html=True)
