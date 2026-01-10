import streamlit as st
import pandas as pd
import time
import subprocess
import sys
import json
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
from src.services.auth_service import AuthService
from src.services.client_service import ClientService
from src.services.pricing_config_service import PricingConfigService
from src.services.simulation_service import SimulationService
from pathlib import Path
import os

# -- 1. SYSTEM INITIALIZATION --
@st.cache_resource
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

# -- AUTHENTICATION CHECK --
auth_service = AuthService()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Show login/register if not logged in
if not st.session_state.logged_in:
    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
    auth_tab1, auth_tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with auth_tab1:
        st.markdown("<h2 style='text-align: center; color: #fce303;'>Welcome Back</h2>", unsafe_allow_html=True)
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("LOGIN", use_container_width=True):
            success, message = auth_service.login(login_username, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Login successful!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)
    
    with auth_tab2:
        st.markdown("<h2 style='text-align: center; color: #fce303;'>Create Account</h2>", unsafe_allow_html=True)
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_email = st.text_input("Email (optional)", key="reg_email")
        reg_name = st.text_input("Full Name (optional)", key="reg_name")
        if st.button("REGISTER", use_container_width=True):
            success, message = auth_service.register(reg_username, reg_password, reg_email, reg_name)
            if success:
                st.success("Registration successful! Please login.")
            else:
                st.error(message)
    st.stop()

# User is logged in - show main interface
st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

st.sidebar.markdown("---")
page = st.sidebar.radio("COMMAND NAVIGATION", [
    "🌐 GLOBAL MARKET", 
    "📈 FINANCIAL INTELLIGENCE",
    "👥 CLIENT REGISTRY",
    "⚙️ ADMIN CONTROL"
])

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
            # Enhanced Sales Chart with Revenue and Profit
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['cumulative_profit'],
                mode='lines+markers',
                name='Cumulative Profit',
                line=dict(color='#fce303', width=4),
                fill='tozeroy',
                fillcolor='rgba(252, 227, 3, 0.1)'
            ))
            # Add revenue line
            df['cumulative_revenue'] = df['total_revenue'].cumsum()
            fig_line.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['cumulative_revenue'],
                mode='lines',
                name='Cumulative Revenue',
                line=dict(color='#00ff00', width=2, dash='dash')
            ))
            fig_line.update_layout(
                title="EMPIRE EQUITY GROWTH (REAL-TIME)",
                xaxis_title="Time of Transaction",
                yaxis_title="Amount ($)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(x=0, y=1)
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
            st.markdown(f"<div style='text-align:center; color:#888;'>Last Sync: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

        st.subheader("📜 Live Ledger Feed")
        display_cols = ['timestamp', 'order_id', 'destination', 'weight_kg', 'net_profit']
        if 'client_id' in df.columns:
            display_cols.insert(3, 'client_id')
        st.dataframe(df[display_cols].sort_values('timestamp', ascending=False), 
                     use_container_width=True)

# -- 6. CLIENT REGISTRY VIEW --
elif page == "👥 CLIENT REGISTRY":
    client_service = ClientService()
    controller = load_engine()
    history = controller._read_history()
    
    st.markdown("### 👥 Client Registry & Sales History")
    
    clients = client_service.get_all_clients()
    
    if not clients:
        st.info("No clients registered yet. Add clients in Admin Control.")
    else:
        # Client selector
        client_options = {f"{c['name']} ({c['client_id']})": c['client_id'] for c in clients}
        selected_client_display = st.selectbox("Select Client", list(client_options.keys()))
        selected_client_id = client_options[selected_client_display]
        selected_client = client_service.get_client(selected_client_id)
        
        if selected_client:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {selected_client['name']}")
                st.write(f"**Email:** {selected_client.get('email', 'N/A')}")
                st.write(f"**Phone:** {selected_client.get('phone', 'N/A')}")
                st.write(f"**Address:** {selected_client.get('address', 'N/A')}")
                if selected_client.get('notes'):
                    st.write(f"**Notes:** {selected_client['notes']}")
            
            with col2:
                st.markdown("### Sales Summary")
                client_sales = [h for h in history if h.get('client_id') == selected_client_id]
                total_revenue = sum(s.get('total_revenue', 0) for s in client_sales)
                total_profit = sum(s.get('net_profit', 0) for s in client_sales)
                st.metric("Total Orders", len(client_sales))
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
                st.metric("Total Profit", f"${total_profit:,.2f}")
            
            st.markdown("---")
            st.subheader("Sales History")
            if client_sales:
                sales_df = pd.DataFrame(client_sales)
                sales_df['timestamp'] = pd.to_datetime(sales_df['timestamp'])
                sales_df = sales_df.sort_values('timestamp', ascending=False)
                
                # Display sales with banana images if available
                for idx, sale in sales_df.iterrows():
                    with st.expander(f"Order {sale['order_id']} - {sale['timestamp'].strftime('%Y-%m-%d %H:%M')} - ${sale['net_profit']:,.2f}"):
                        col_img, col_info = st.columns([1, 2])
                        with col_info:
                            st.write(f"**Destination:** {sale['destination']}")
                            st.write(f"**Weight:** {sale['weight_kg']} kg")
                            st.write(f"**Tier:** {sale['tier_sold']}")
                            st.write(f"**Revenue:** ${sale['total_revenue']:,.2f}")
                            st.write(f"**Profit:** ${sale['net_profit']:,.2f}")
                        with col_img:
                            batch_id = sale.get('batch_id', '')
                            results_dir = Path("data/results")
                            
                            # Try to find an image that contains the batch ID in the filename
                            # e.g., "batch_309ee39f_analysis.jpg"
                            image_files = list(results_dir.glob(f"*{batch_id}*.jpg"))
                            
                            if image_files:
                                st.image(str(image_files[0]), caption=f"Batch {batch_id} Scan", width=300)
                            else:
                                # Fallback to a placeholder or the first available image
                                all_images = list(results_dir.glob("*.jpg"))
                                if all_images:
                                    st.image(str(all_images[0]), caption="Representative Sample", width=300)
                                else:
                                    st.warning("No Scan Found")
            else:
                st.info("No sales recorded for this client.")

# -- 7. ADMIN CONTROL PANEL --
elif page == "⚙️ ADMIN CONTROL":
    st.markdown("### ⚙️ Admin Control Panel")
    
    admin_tabs = st.tabs(["👥 Clients", "💰 Pricing", "📊 Sales", "🚚 Shipments", "🎲 Simulation"])
    
    client_service = ClientService()
    pricing_service = PricingConfigService()
    controller = load_engine()
    simulation_service = SimulationService()
    
    # CLIENTS TAB
    with admin_tabs[0]:
        st.subheader("Client Management")
        crud_action = st.radio("Action", ["Create", "View/Edit", "Delete"], horizontal=True)
        
        # Create
        if crud_action == "Create":
            with st.form("create_client"):
                name = st.text_input("Client Name *")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                address = st.text_area("Address")
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Create Client")
                
                if submitted:
                    # MANUAL VALIDATION
                    if not name:
                        st.error("🛑 Error: Client Name is required!")
                    else:
                        client = client_service.create_client(name, email, phone, address, notes)
                        st.success(f"✅ Client {client['client_id']} created!")
                        time.sleep(1)
                        st.rerun()
        
        elif crud_action == "View/Edit":
            clients = client_service.get_all_clients()
            if clients:
                client_options = {f"{c['name']} ({c['client_id']})": c['client_id'] for c in clients}
                selected = st.selectbox("Select Client", list(client_options.keys()))
                client_id = client_options[selected]
                client = client_service.get_client(client_id)
                
                if client:
                    with st.form("edit_client"):
                        name = st.text_input("Name", value=client.get('name', ''))
                        email = st.text_input("Email", value=client.get('email', ''))
                        phone = st.text_input("Phone", value=client.get('phone', ''))
                        address = st.text_area("Address", value=client.get('address', ''))
                        notes = st.text_area("Notes", value=client.get('notes', ''))
                        if st.form_submit_button("Update Client"):
                            client_service.update_client(client_id, name=name, email=email, 
                                                         phone=phone, address=address, notes=notes)
                            st.success("Client updated!")
                            time.sleep(1)
                            st.rerun()
            else:
                st.info("No clients to edit.")
        
        elif crud_action == "Delete":
            clients = client_service.get_all_clients()
            if clients:
                client_options = {f"{c['name']} ({c['client_id']})": c['client_id'] for c in clients}
                selected = st.selectbox("Select Client to Delete", list(client_options.keys()))
                client_id = client_options[selected]
                if st.button("Delete Client", type="primary"):
                    if client_service.delete_client(client_id):
                        st.success("Client deleted!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.info("No clients to delete.")
    
    # PRICING TAB
    with admin_tabs[1]:
        st.subheader("Pricing Configuration")
        config = pricing_service.get_config()
        
        st.markdown("#### Base Pricing")
        base_price = st.number_input("Base Price per KG ($)", value=config.get('base_price_per_kg', 1.35), 
                                     min_value=0.01, step=0.01)
        if st.button("Update Base Price"):
            pricing_service.update_base_price(base_price)
            st.success("Base price updated!")
            time.sleep(1)
            st.rerun()
        
        st.markdown("---")
        st.markdown("#### Tier Pricing")
        tier_tabs = st.tabs(["Premium", "Standard", "Economic"])
        
        for idx, tier in enumerate(["premium", "standard", "economic"]):
            with tier_tabs[idx]:
                tier_config = config.get(tier, {})
                margin = st.number_input(f"Margin Multiplier", 
                                        value=tier_config.get('margin_multiplier', 1.2), 
                                        min_value=1.0, step=0.01, key=f"margin_{tier}")
                quality = st.number_input(f"Quality Bonus Multiplier", 
                                         value=tier_config.get('quality_bonus_multiplier', 1.0), 
                                         min_value=0.0, step=0.01, key=f"quality_{tier}")
                if st.button(f"Update {tier.title()} Pricing", key=f"btn_{tier}"):
                    pricing_service.update_tier_pricing(tier, margin_multiplier=margin, 
                                                        quality_bonus_multiplier=quality)
                    st.success(f"{tier.title()} pricing updated!")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### Shipping Costs")
        shipping = config.get('shipping', {})
        destinations = ["USA", "GERMANY", "SPAIN", "CHINA", "LOCAL"]
        for dest in destinations:
            cost = st.number_input(f"{dest} ($/kg)", value=shipping.get(dest, 1.0), 
                                   min_value=0.01, step=0.01, key=f"ship_{dest}")
            if st.button(f"Update {dest}", key=f"ship_btn_{dest}"):
                pricing_service.update_shipping_cost(dest, cost)
                st.success(f"{dest} shipping cost updated!")
                time.sleep(1)
                st.rerun()
    
    # SALES TAB
    with admin_tabs[2]:
        st.subheader("Sales Management")
        history = controller._read_history()
        
        if history:
            df = pd.DataFrame(history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                date_range = st.date_input("Date Range", 
                                          value=[df['timestamp'].min().date(), df['timestamp'].max().date()],
                                          min_value=df['timestamp'].min().date(),
                                          max_value=df['timestamp'].max().date())
            with col2:
                tier_filter = st.multiselect("Filter by Tier", ["PREMIUM", "STANDARD", "ECONOMIC"], 
                                            default=["PREMIUM", "STANDARD", "ECONOMIC"])
            
            # Apply filters
            filtered_df = df[df['tier_sold'].isin(tier_filter)]
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['timestamp'].dt.date >= date_range[0]) & 
                    (filtered_df['timestamp'].dt.date <= date_range[1])
                ]
            
            st.dataframe(filtered_df[['timestamp', 'order_id', 'destination', 'tier_sold', 
                                      'weight_kg', 'total_revenue', 'net_profit']].sort_values('timestamp', ascending=False),
                        use_container_width=True)
            
            # Edit/Delete sales
            st.markdown("### Edit/Delete Sale")
            sale_options = {f"{s['order_id']} - {s['timestamp'][:10]}": s['order_id'] for s in history}
            selected_sale = st.selectbox("Select Sale", list(sale_options.keys()))
            sale_id = sale_options[selected_sale]
            sale = next((s for s in history if s['order_id'] == sale_id), None)
            
            if sale:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Delete Sale"):
                        history = [h for h in history if h['order_id'] != sale_id]
                        with open(controller.history_path, 'w') as f:
                            json.dump(history, f, indent=2)
                        st.success("Sale deleted!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("No sales recorded.")
    
    # SHIPMENTS TAB
    with admin_tabs[3]:
        st.subheader("Shipment Management")
        history = controller._read_history()
        
        if history:
            shipments_df = pd.DataFrame(history)
            shipments_df['timestamp'] = pd.to_datetime(shipments_df['timestamp'])
            
            st.dataframe(shipments_df[['timestamp', 'order_id', 'destination', 'weight_kg', 
                                      'shipping_cost', 'tier_sold']].sort_values('timestamp', ascending=False),
                        use_container_width=True)
            
            # Shipment statistics
            st.markdown("### Shipment Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Shipments", len(shipments_df))
            with col2:
                st.metric("Total Weight Shipped", f"{shipments_df['weight_kg'].sum():,.2f} kg")
            with col3:
                st.metric("Total Shipping Cost", f"${shipments_df['shipping_cost'].sum():,.2f}")
        else:
            st.info("No shipments recorded.")
    
    # SIMULATION TAB
    with admin_tabs[4]:
        st.subheader("Historical Sales Simulation")
        st.markdown("Generate simulated sales data between 2026-02-01 and 2028-02-01")
        
        col1, col2 = st.columns(2)
        with col1:
            num_orders = st.number_input("Number of Orders", min_value=1, max_value=10000, value=100)
        with col2:
            start_date = st.date_input("Start Date", value=datetime(2026, 2, 1).date())
            end_date = st.date_input("End Date", value=datetime(2028, 2, 1).date())
        
        # Get client IDs for assignment
        clients = client_service.get_all_clients()
        client_ids = [c['client_id'] for c in clients] if clients else None
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Simulated Sales", type="primary"):
                with st.spinner("Generating simulated sales..."):
                    count = simulation_service.add_simulated_sales_to_history(
                        num_orders=num_orders,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        client_ids=client_ids,
                        clear_existing=False
                    )
                    st.success(f"Generated {count} simulated sales!")
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            if st.button("Clear All Simulated Sales"):
                with st.spinner("Clearing simulated sales..."):
                    count = simulation_service.clear_simulated_sales()
                    st.success(f"Removed {count} simulated sales!")
                    time.sleep(1)
                    st.rerun()
        
        # Show simulation status
        history = controller._read_history()
        simulated_count = sum(1 for h in history if h.get('simulated', False))
        real_count = len(history) - simulated_count
        st.info(f"Current status: {real_count} real sales, {simulated_count} simulated sales")