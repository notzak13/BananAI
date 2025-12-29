import streamlit as st
import pandas as pd
import time
import subprocess
import sys
from datetime import datetime

# --- AUTOMATIC DEPENDENCY CHECK ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px
    import plotly.graph_objects as go

from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory
from src.controller.order_controller import OrderController
from src.services.inventory_manager import InventoryManager

# -- 1. SYSTEM INITIALIZATION --
def load_engine():
    repo = BatchRepository()
    inv = Inventory()
    for b in repo.load_all_batches():
        inv.add_batch(b)
    return OrderController(inv, repo)

st.set_page_config(page_title="BananAI | Global ERP", page_icon="🍌", layout="wide")

# -- 2. THE "EMPIRE" STYLING (Glassmorphism & Gold Theme) --
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #2a2a2a, #121212);
    }

    /* Metric Cards Custom Look */
    div[data-testid="stMetric"] {
        background: rgba(252, 227, 3, 0.05);
        border: 1px solid rgba(252, 227, 3, 0.3);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #fce303 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.8rem !important;
    }

    /* Custom Container for Batches */
    .batch-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .batch-card:hover {
        border-color: #fce303;
        background: rgba(252, 227, 3, 0.02);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #fce303 0%, #e5cf02 100%);
        color: #1a1a1a !important;
        border: none;
        padding: 12px 24px;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 10px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(252, 227, 3, 0.4);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 1px solid rgba(252, 227, 3, 0.2);
    }

    /* Pulsing Online Dot */
    .online-indicator {
        height: 10px;
        width: 10px;
        background-color: #00ff00;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px #00ff00;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        70% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    </style>
    """, unsafe_allow_html=True)

# -- 3. HEADER & LOGO --
col_logo, col_status = st.columns([4, 1])
with col_logo:
    st.markdown("<h1 style='color: #fce303; margin-bottom: 0;'>BANANAI <span style='color: white; font-weight: 100;'>ENTERPRISE</span></h1>", unsafe_allow_html=True)
    st.caption("Quantum-Inspection & Global Logistics ERP v3.0")
with col_status:
    st.markdown("<div style='text-align: right; padding-top: 25px;'><span class='online-indicator'></span><span style='color: #00ff00;'>CORE ENGINE LIVE</span></div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
page = st.sidebar.radio("COMMAND NAVIGATION", ["🌐 GLOBAL MARKET", "📈 FINANCIAL INTELLIGENCE"])

# -- 4. BUYER PORTAL (The "Global Market" View) --
if page == "🌐 GLOBAL MARKET":
    controller = load_engine()
    
    # Hero Section
    st.markdown("### 🌎 Global Export Fulfillment")
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        dest = st.selectbox("🎯 TARGET DESTINATION", ["USA", "GERMANY", "SPAIN", "CHINA", "LOCAL"])
    with c2:
        weight = st.number_input("⚖️ REQUIRED MASS (KG)", min_value=1.0, value=500.0)
    with c3:
        tier = st.selectbox("💎 QUALITY TIER", ["Premium", "Standard", "Economic"])

    st.markdown("---")

    proposals = controller.get_proposals(dest, weight, tier)
    matches = proposals['perfect'] + proposals['alternatives']

    if not matches:
        st.warning("🚨 SYSTEM ALERT: No batches found matching the transit shelf-life requirements.")
    else:
        for b in matches:
            invoice = controller.generate_invoice(b, weight, dest, tier)
            
            # Custom HTML Card
            with st.container():
                st.markdown(f"""
                <div class="batch-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #fce303; font-weight: 900; font-size: 1.5rem;">BATCH #{b.batch_id}</span>
                            <p style="color: #888; margin:0;">AI Quality Score: {b.average_quality():.2f} | Life: {b.estimated_shelf_life_days()} Days</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: white; font-size: 0.8rem; display: block;">INVOICE TOTAL</span>
                            <span style="color: #fce303; font-size: 1.8rem; font-weight: 900;">${invoice['total_revenue']:,.2f}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Buttons inside a Column (Streamlit components can't go in f-strings)
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 1, 1, 1.2])
                with btn_col1:
                    st.progress(b.remaining_weight_kg / b.total_weight_kg if b.total_weight_kg > 0 else 0, text=f"Stock: {b.remaining_weight_kg:,.0f}kg left")
                with btn_col4:
                    if st.button(f"EXECUTE TRADE #{b.batch_id}", use_container_width=True):
                        if controller.commit_transaction(invoice, b):
                            st.balloons()
                            st.toast(f"Trade ORD-{b.batch_id} complete!", icon="✅")
                            time.sleep(1)
                            st.rerun()

# -- 5. ADMIN COMMAND CENTER (The "Financial Intelligence" View) --
elif page == "📈 FINANCIAL INTELLIGENCE":
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        auth_col_1, auth_col_2, auth_col_3 = st.columns([1, 2, 1])
        with auth_col_2:
            st.markdown("<h3 style='text-align: center;'>🔐 ENCRYPTED ACCESS</h3>", unsafe_allow_html=True)
            pw = st.text_input("Enter Admin Credentials", type="password", help="Contact System Architect for access.")
            if st.button("AUTHORIZE"):
                if pw == "zak123!":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("INVALID CREDENTIALS")
    else:
        controller = load_engine()
        summary = controller.get_financial_summary()
        history = controller._read_history()

        # High-Level KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("GROSS REVENUE", f"${summary['revenue']:,.2f}", delta="Global Sales")
        kpi2.metric("NET PROFIT", f"${summary['profit']:,.2f}", delta="After Logistics")
        margin = (summary['profit']/summary['revenue']*100 if summary['revenue']>0 else 0)
        kpi3.metric("EFFICIENCY", f"{margin:.1f}%", delta="Margin")
        kpi4.metric("LOGISTICS", summary['orders'], delta="Shipments")

        # Visual Intelligence Section
        if history:
            df = pd.DataFrame(history)
            # Ensure timestamp is datetime for "Stocks" line chart
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            # Calculate cumulative profit over time
            df['cumulative_profit'] = df['net_profit'].cumsum()
            
            st.markdown("---")
            chart_col, dist_col = st.columns([2, 1])
            
            with chart_col:
                # "THE STOCKS CHART" - Cumulative Profit Growth
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=df['timestamp'], 
                    y=df['cumulative_profit'],
                    mode='lines+markers',
                    name='Equity Curve',
                    line=dict(color='#fce303', width=4),
                    fill='tozeroy',
                    fillcolor='rgba(252, 227, 3, 0.1)'
                ))
                fig_line.update_layout(
                    title="EMPIRE EQUITY GROWTH (REAL-TIME)",
                    xaxis_title="Time of Transaction",
                    yaxis_title="Total Cumulative Profit ($)",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            with dist_col:
                # MARKET DISTRIBUTION SPREAD
                fig_sun = px.sunburst(
                    df, 
                    path=['destination', 'tier_sold'], 
                    values='net_profit',
                    title="MARKET PENETRATION",
                    color_continuous_scale='Greens',
                    template="plotly_dark"
                )
                fig_sun.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_sun, use_container_width=True)

            # Operations Row
            st.markdown("---")
            ops_col1, ops_col2, ops_col3 = st.columns([1, 1, 1])
            with ops_col1:
                if st.button("🧹 ARCHIVE EXHAUSTED"):
                    with st.spinner("Optimizing Warehouse..."):
                        count = InventoryManager.archive_empty_batches()
                        st.success(f"Archived {count} batches.")
                        time.sleep(1)
                        st.rerun()
            with ops_col2:
                 st.download_button("📥 EXPORT LEDGER (CSV)", 
                                   data=df.to_csv(index=False), 
                                   file_name="BananAI_Ledger.csv",
                                   mime="text/csv",
                                   use_container_width=True)
            with ops_col3:
                # Just a decorative metric to fill space
                st.markdown(f"<div style='text-align:center; color:#888;'>Last Sync: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

            st.subheader("📜 Live Ledger Feed")
            st.dataframe(df[['timestamp', 'order_id', 'destination', 'weight_kg', 'net_profit']].sort_values('timestamp', ascending=False), 
                         use_container_width=True)
        
        if st.sidebar.button("TERMINATE SESSION"):
            st.session_state.auth = False
            st.rerun()