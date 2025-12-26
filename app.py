import streamlit as st
import pandas as pd
import time
import subprocess
import sys
from datetime import datetime

# --- AUTOMATIC DEPENDENCY CHECK (Presentation Insurance) ---
try:
    import plotly.express as px
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px

from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory
from src.controller.order_controller import OrderController
from src.services.inventory_manager import InventoryManager

# -- 1. SYSTEM INITIALIZATION --
def load_engine():
    """Ensures the UI is always synced with the latest disk data."""
    repo = BatchRepository()
    inv = Inventory()
    for b in repo.load_all_batches():
        inv.add_batch(b)
    return OrderController(inv, repo)

st.set_page_config(page_title="BananAI Global ERP", page_icon="🍌", layout="wide")

# -- 2. VISIBILITY & BRANDING FIX (The 'Dark Mode' Killer) --
st.markdown("""
    <style>
    /* Force metrics to be readable in Dark or Light mode */
    [data-testid="stMetric"] {
        background-color: #fce303 !important;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #e5cf02;
    }
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-size: 1.1rem !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# -- 3. NAVIGATION --
st.sidebar.title("🍌 BananAI Systems")
st.sidebar.caption("Enterprise Edition v2.2")
page = st.sidebar.radio("Navigate", ["🌐 Buyer Portal", "📈 Admin Command Center"])

# -- 4. BUYER PORTAL --
if page == "🌐 Buyer Portal":
    controller = load_engine()
    st.title("🌐 Global Export Fulfillment")
    st.write("Live brokerage interface for international trade.")

    with st.sidebar.expander("Order Specifications", expanded=True):
        dest = st.selectbox("Destination", ["USA", "GERMANY", "SPAIN", "CHINA", "LOCAL"])
        weight = st.number_input("Order Weight (kg)", min_value=1.0, value=500.0)
        tier = st.selectbox("Quality Tier", ["Premium", "Standard", "Economic"])

    proposals = controller.get_proposals(dest, weight, tier)
    matches = proposals['perfect'] + proposals['alternatives']

    if not matches:
        st.error("⚠️ Logistics Alert: No batches meet the shelf-life requirements for this route.")
    else:
        st.subheader(f"Optimal Batches for {dest}")
        for b in matches:
            with st.container(border=True):
                col_info, col_price, col_action = st.columns([2, 1, 1])
                invoice = controller.generate_invoice(b, weight, dest, tier)
                
                with col_info:
                    st.markdown(f"### Batch {b.batch_id}")
                    st.write(f"**Quality Score:** {b.average_quality():.2f}")
                    st.write(f"**Stock Available:** {b.remaining_weight_kg:,.1f} kg")
                    st.caption(f"Estimated Shelf Life: {b.estimated_shelf_life_days()} days")
                
                with col_price:
                    st.metric("Unit Price", f"${invoice['unit_price']}/kg")
                    st.write(f"Total Value: **${invoice['total_revenue']:,.2f}**")

                with col_action:
                    st.write(" ") # Spacer
                    if st.button(f"Confirm & Book", key=f"book_{b.batch_id}"):
                        if controller.commit_transaction(invoice, b):
                            st.balloons()
                            st.success(f"Order {invoice['order_id']} Booked!")
                            st.toast("Manifest Generated!", icon="📄")
                            time.sleep(1.5)
                            st.rerun()

# -- 5. ADMIN COMMAND CENTER --
elif page == "📈 Admin Command Center":
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Secure Authentication")
        pw = st.text_input("Admin Password", type="password")
        if st.button("Unlock Dashboard"):
            if pw == "zak123!":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied.")
    else:
        controller = load_engine()
        summary = controller.get_financial_summary()
        history = controller._read_history()

        st.title("Empire Financial Intelligence")
        
        # Financial Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross Revenue", f"${summary['revenue']:,.2f}")
        m2.metric("Net Profit", f"${summary['profit']:,.2f}")
        m3.metric("Profit Margin", f"{(summary['profit']/summary['revenue']*100 if summary['revenue']>0 else 0):.1f}%")
        m4.metric("Total Orders", summary['orders'])

        # Chart Logic
        if history:
            df = pd.DataFrame(history)
            st.divider()
            col_chart, col_cleanup = st.columns([3, 1])
            
            with col_chart:
                fig = px.bar(df, x="destination", y="net_profit", color="tier_sold", 
                             title="Profitability by Global Market", barmode="group",
                             template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_cleanup:
                st.write("### Warehouse Ops")
                if st.button("🧹 Archive Depleted"):
                    count = InventoryManager.archive_empty_batches()
                    st.success(f"Archived {count} batches.")
                    time.sleep(1)
                    st.rerun()

            st.subheader("Transaction Ledger")
            st.dataframe(df[['timestamp', 'order_id', 'destination', 'weight_kg', 'net_profit']], use_container_width=True)
        
        if st.sidebar.button("Logout"):
            st.session_state.auth = False
            st.rerun()