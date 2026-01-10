import os
import time
import getpass
import json
from typing import Dict, Any
from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory
from src.controller.order_controller import OrderController
from src.services.inventory_manager import InventoryManager
from src.services.auth_service import AuthService
from src.services.client_service import ClientService
from src.services.pricing_config_service import PricingConfigService
from src.services.simulation_service import SimulationService

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Standardized Branding for the Empire."""
    width = 70
    print("\n" + "╔" + "═" * (width-2) + "╗")
    print(f"║ {title:^66} ║")
    print("╚" + "═" * (width-2) + "╝")

def buyer_portal(controller: OrderController):
    clear_screen()
    print_header("🍌 BANANAI BUYER PORTAL | GLOBAL LOGISTICS")
    
    # 1. Logistics Input
    print("\n[ Step 1: Destination & Volume ]")
    print("Available Routes: USA, Germany, Spain, China, Local")
    dest = input("  ➤ Destination: ").upper() or "LOCAL"
    
    try:
        weight_input = input("  ➤ Quantity (kg): ")
        weight = float(weight_input) if weight_input else 0.0
    except ValueError:
        print("\n❌ FORMAT ERROR: Mass must be numeric.")
        time.sleep(1.5)
        return

    # 2. Quality Filter
    print("\n[ Step 2: Quality Preference ]")
    print("  [P] Premium  (High Quality Scans)")
    print("  [S] Standard (Balance)")
    print("  [E] Economic (Any)")
    tier_choice = input("\n  ➤ Selection: ").lower()
    tier = "premium" if tier_choice == 'p' else "economic" if tier_choice == 'e' else "standard"

    # 3. Matchmaking Engine
    proposals = controller.get_proposals(dest, weight, tier)
    matches = proposals['perfect'] + proposals['alternatives']
    
    if not matches:
        print("\n" + "!" * 70)
        print("  CRITICAL: NO VIABLE STOCK FOUND FOR THIS ROUTE/TIER.")
        print("!" * 70)
        input("\nPress Enter to return...")
        return

    print(f"\n{'REF #' :<6} | {'QUALITY' :<10} | {'SHELF LIFE' :<12} | {'AVAILABILITY'}")
    print("─" * 70)
    
    for i, b in enumerate(matches, 1):
        # UI Polish: Visual quality bar
        q_val = b.average_quality()
        q_bar = "■" * int(q_val * 10)
        status = "⭐" if b in proposals['perfect'] else "  "
        
        print(f"  ({i:02})   | {q_val:.2f} {q_bar:<10} | {b.estimated_shelf_life_days():>2} Days Left | {b.remaining_weight_kg:,.1f} kg {status}")

    # 4. Transaction Initialization
    try:
        selection = input("\n  ➤ Select Ref # to book manifest (0 to cancel): ")
        if not selection.isdigit() or int(selection) == 0: return
        selected_batch = matches[int(selection)-1]
    except (ValueError, IndexError):
        print("❌ Selection out of range.")
        time.sleep(1)
        return

    # Optional: Select client
    client_service = ClientService()
    clients = client_service.get_all_clients()
    client_id = None
    if clients:
        print("\n[ Optional: Assign to Client ]")
        print("  [0] No client")
        for i, c in enumerate(clients, 1):
            print(f"  [{i}] {c['name']} ({c['client_id']})")
        try:
            client_choice = input("\n  ➤ Select client (0 to skip): ")
            if client_choice.isdigit() and int(client_choice) > 0:
                client_id = clients[int(client_choice)-1]['client_id']
        except (ValueError, IndexError):
            pass
    
    invoice = controller.generate_invoice(selected_batch, weight, dest, tier, client_id)

    # 5. The eBOL Preview
    clear_screen()
    print_header("🧾 ELECTRONIC BILL OF LADING (MANIFEST)")
    print(f"  ORDER REF:    {invoice['order_id']}")
    print(f"  COMMODITY:    Cavendish ({invoice['tier_sold'].upper()})")
    print(f"  ORIGIN:       BananaI Hub")
    print(f"  DESTINATION:  {invoice['destination']}")
    print(f"  MASS:         {invoice['weight_kg']:,} kg")
    print("─" * 70)
    print(f"  UNIT PRICE:   ${invoice['unit_price']:.2f} USD/kg")
    print(f"  GRAND TOTAL:  ${invoice['total_revenue']:,.2f} USD")
    print("─" * 70)

    confirm = input("\n  ➤ Confirm Transaction? (y/n): ").lower()
    if confirm == 'y':
        success = controller.commit_transaction(invoice, selected_batch)
        if success:
            print("\n✅ SHIPMENT BOOKED. Ledger updated. Manifest generated in data/orders/.")
        else:
            print("\n❌ ERROR: Batch depletion conflict. Try a different batch.")
    
    input("\nPress Enter to return to Main Terminal...")

def login_register():
    """Handle login/register in terminal with persistent loop."""
    auth_service = AuthService()
    
    while True:
        clear_screen()
        print_header("🔐 BANANAI AUTHENTICATION")
        
        print("\n  [1] Login")
        print("  [2] Register")
        print("  [3] Exit System")
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            username = input("  ➤ Username: ")
            password = getpass.getpass("  ➤ Password: ")
            success, message = auth_service.login(username, password)
            if success:
                print(f"\n✅ {message}")
                time.sleep(1)
                return username
            else:
                print(f"\n❌ {message}")
                time.sleep(2)
                # Loop continues, bringing them back to the menu
        
        elif choice == "2":
            username = input("  ➤ Username: ")
            password = getpass.getpass("  ➤ Password: ")
            email = input("  ➤ Email (optional): ")
            full_name = input("  ➤ Full Name (optional): ")
            success, message = auth_service.register(username, password, email, full_name)
            if success:
                print(f"\n✅ {message}")
                time.sleep(1)
                # We return the username so they are logged in immediately
                return username
            else:
                print(f"\n❌ {message}")
                time.sleep(2)
                # Loop continues
        
        elif choice == "3":
            print("\n[SYSTEM] Shutting down...")
            exit() # Hard exit for the 'Exit' option

def manage_clients(client_service: ClientService):
    """CRUD operations for clients in terminal."""
    while True:
        clear_screen()
        print_header("👥 CLIENT MANAGEMENT")
        print("\n  [1] Create Client")
        print("  [2] List All Clients")
        print("  [3] View/Edit Client")
        print("  [4] Delete Client")
        print("  [5] Search Clients")
        print("  [6] Back to Admin")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            clear_screen()
            print_header("CREATE CLIENT")
            name = input("  ➤ Client Name: ")
            email = input("  ➤ Email: ")
            phone = input("  ➤ Phone: ")
            address = input("  ➤ Address: ")
            notes = input("  ➤ Notes: ")
            client = client_service.create_client(name, email, phone, address, notes)
            print(f"\n✅ Client {client['client_id']} created!")
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            clear_screen()
            print_header("ALL CLIENTS")
            clients = client_service.get_all_clients()
            if not clients:
                print("\n  [!] No clients found.")
            else:
                print(f"{'ID' :<12} | {'NAME' :<20} | {'EMAIL' :<25} | {'PHONE'}")
                print("─" * 80)
                for c in clients:
                    print(f"{c['client_id']} | {c['name']:<20} | {c.get('email', 'N/A'):<25} | {c.get('phone', 'N/A')}")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            clear_screen()
            print_header("EDIT CLIENT")
            clients = client_service.get_all_clients()
            if not clients:
                print("\n  [!] No clients found.")
                input("\nPress Enter to continue...")
                continue
            
            for i, c in enumerate(clients, 1):
                print(f"  [{i}] {c['name']} ({c['client_id']})")
            try:
                sel = int(input("\n  ➤ Select client number: ")) - 1
                client = clients[sel]
                print(f"\nEditing: {client['name']}")
                name = input(f"  ➤ Name [{client['name']}]: ") or client['name']
                email = input(f"  ➤ Email [{client.get('email', '')}]: ") or client.get('email', '')
                phone = input(f"  ➤ Phone [{client.get('phone', '')}]: ") or client.get('phone', '')
                address = input(f"  ➤ Address [{client.get('address', '')}]: ") or client.get('address', '')
                notes = input(f"  ➤ Notes [{client.get('notes', '')}]: ") or client.get('notes', '')
                client_service.update_client(client['client_id'], name=name, email=email, 
                                            phone=phone, address=address, notes=notes)
                print("\n✅ Client updated!")
            except (ValueError, IndexError):
                print("\n❌ Invalid selection.")
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            clear_screen()
            print_header("DELETE CLIENT")
            clients = client_service.get_all_clients()
            if not clients:
                print("\n  [!] No clients found.")
                input("\nPress Enter to continue...")
                continue
            
            for i, c in enumerate(clients, 1):
                print(f"  [{i}] {c['name']} ({c['client_id']})")
            try:
                sel = int(input("\n  ➤ Select client number to delete: ")) - 1
                client = clients[sel]
                confirm = input(f"  ➤ Delete {client['name']}? (yes/no): ").lower()
                if confirm == 'yes':
                    if client_service.delete_client(client['client_id']):
                        print("\n✅ Client deleted!")
                    else:
                        print("\n❌ Failed to delete client.")
            except (ValueError, IndexError):
                print("\n❌ Invalid selection.")
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            clear_screen()
            print_header("SEARCH CLIENTS")
            query = input("  ➤ Search term: ")
            results = client_service.search_clients(query)
            if not results:
                print("\n  [!] No matches found.")
            else:
                print(f"{'ID' :<12} | {'NAME' :<20} | {'EMAIL' :<25}")
                print("─" * 60)
                for c in results:
                    print(f"{c['client_id']} | {c['name']:<20} | {c.get('email', 'N/A'):<25}")
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            break

def manage_pricing(pricing_service: PricingConfigService):
    """Manage pricing configuration in terminal."""
    while True:
        clear_screen()
        print_header("💰 PRICING CONFIGURATION")
        config = pricing_service.get_config()
        
        print(f"\n  Base Price per KG: ${config.get('base_price_per_kg', 1.35):.2f}")
        print("\n  Tier Pricing:")
        for tier in ['premium', 'standard', 'economic']:
            tier_config = config.get(tier, {})
            print(f"    {tier.upper()}: Margin={tier_config.get('margin_multiplier', 1.2):.2f}, "
                  f"Quality Bonus={tier_config.get('quality_bonus_multiplier', 1.0):.2f}")
        
        print("\n  Shipping Costs:")
        shipping = config.get('shipping', {})
        for dest, cost in shipping.items():
            print(f"    {dest}: ${cost:.2f}/kg")
        
        print("\n  [1] Update Base Price")
        print("  [2] Update Tier Pricing")
        print("  [3] Update Shipping Cost")
        print("  [4] Back to Admin")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            price = float(input("  ➤ New base price per KG: $"))
            pricing_service.update_base_price(price)
            print("\n✅ Base price updated!")
            time.sleep(1)
        
        elif choice == "2":
            tier = input("  ➤ Tier (premium/standard/economic): ").lower()
            if tier in ['premium', 'standard', 'economic']:
                margin = float(input("  ➤ Margin multiplier: "))
                quality = float(input("  ➤ Quality bonus multiplier: "))
                pricing_service.update_tier_pricing(tier, margin_multiplier=margin, 
                                                    quality_bonus_multiplier=quality)
                print("\n✅ Tier pricing updated!")
            else:
                print("\n❌ Invalid tier.")
            time.sleep(1)
        
        elif choice == "3":
            dest = input("  ➤ Destination (USA/GERMANY/SPAIN/CHINA/LOCAL): ").upper()
            cost = float(input("  ➤ Cost per KG: $"))
            pricing_service.update_shipping_cost(dest, cost)
            print("\n✅ Shipping cost updated!")
            time.sleep(1)
        
        elif choice == "4":
            break

def manage_sales(controller: OrderController):
    """Manage sales in terminal."""
    while True:
        clear_screen()
        print_header("📊 SALES MANAGEMENT")
        history = controller._read_history()
        
        if history:
            print(f"\n  Total Sales: {len(history)}")
            total_revenue = sum(h.get('total_revenue', 0) for h in history)
            total_profit = sum(h.get('net_profit', 0) for h in history)
            print(f"  Total Revenue: ${total_revenue:,.2f}")
            print(f"  Total Profit: ${total_profit:,.2f}")
        
        print("\n  [1] View All Sales")
        print("  [2] View Sales by Client")
        print("  [3] Delete Sale")
        print("  [4] Back to Admin")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            clear_screen()
            print_header("ALL SALES")
            if not history:
                print("\n  [!] No sales found.")
            else:
                print(f"{'DATE' :<16} | {'ID' :<12} | {'DEST' :<10} | {'WEIGHT' :<10} | {'PROFIT'}")
                print("─" * 80)
                for order in history[-50:]:  # Show last 50
                    print(f"{order['timestamp'][:16]} | {order['order_id']} | "
                          f"{order['destination']:<10} | {order['weight_kg']:>8.2f}kg | "
                          f"${order['net_profit']:>10,.2f}")
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            clear_screen()
            print_header("SALES BY CLIENT")
            client_service = ClientService()
            clients = client_service.get_all_clients()
            if not clients:
                print("\n  [!] No clients found.")
            else:
                for i, c in enumerate(clients, 1):
                    print(f"  [{i}] {c['name']} ({c['client_id']})")
                try:
                    sel = int(input("\n  ➤ Select client: ")) - 1
                    client = clients[sel]
                    client_sales = [h for h in history if h.get('client_id') == client['client_id']]
                    if client_sales:
                        print(f"\n  Sales for {client['name']}:")
                        print(f"{'DATE' :<16} | {'ID' :<12} | {'PROFIT'}")
                        print("─" * 50)
                        for sale in client_sales:
                            print(f"{sale['timestamp'][:16]} | {sale['order_id']} | ${sale['net_profit']:>10,.2f}")
                    else:
                        print("\n  [!] No sales for this client.")
                except (ValueError, IndexError):
                    print("\n❌ Invalid selection.")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            clear_screen()
            print_header("DELETE SALE")
            if not history:
                print("\n  [!] No sales found.")
                input("\nPress Enter to continue...")
                continue
            
            for i, sale in enumerate(history[-20:], 1):  # Show last 20
                print(f"  [{i}] {sale['order_id']} - {sale['timestamp'][:10]} - ${sale['net_profit']:,.2f}")
            try:
                sel = int(input("\n  ➤ Select sale number: ")) - 1
                sale = history[-(20-sel) if sel < 20 else sel]
                confirm = input(f"  ➤ Delete {sale['order_id']}? (yes/no): ").lower()
                if confirm == 'yes':
                    history = [h for h in history if h['order_id'] != sale['order_id']]
                    with open(controller.history_path, 'w') as f:
                        json.dump(history, f, indent=2)
                    print("\n✅ Sale deleted!")
            except (ValueError, IndexError):
                print("\n❌ Invalid selection.")
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            break

def manage_simulation(simulation_service: SimulationService, controller: OrderController):
    """Manage historical sales simulation in terminal."""
    while True:
        clear_screen()
        print_header("🎲 HISTORICAL SALES SIMULATION")
        history = controller._read_history()
        simulated_count = sum(1 for h in history if h.get('simulated', False))
        real_count = len(history) - simulated_count
        
        print(f"\n  Current Status:")
        print(f"    Real Sales: {real_count}")
        print(f"    Simulated Sales: {simulated_count}")
        
        print("\n  [1] Generate Simulated Sales")
        print("  [2] Clear All Simulated Sales")
        print("  [3] Back to Admin")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            clear_screen()
            print_header("GENERATE SIMULATED SALES")
            num_orders = int(input("  ➤ Number of orders: "))
            start_date = input("  ➤ Start date (YYYY-MM-DD) [2026-02-01]: ") or "2026-02-01"
            end_date = input("  ➤ End date (YYYY-MM-DD) [2028-02-01]: ") or "2028-02-01"
            
            client_service = ClientService()
            clients = client_service.get_all_clients()
            client_ids = [c['client_id'] for c in clients] if clients else None
            
            clear_existing = input("  ➤ Clear existing simulated sales? (yes/no) [no]: ").lower() == 'yes'
            
            print("\n  Generating...")
            count = simulation_service.add_simulated_sales_to_history(
                num_orders=num_orders,
                start_date=start_date,
                end_date=end_date,
                client_ids=client_ids,
                clear_existing=clear_existing
            )
            print(f"\n✅ Generated {count} simulated sales!")
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            confirm = input("  ➤ Clear all simulated sales? (yes/no): ").lower()
            if confirm == 'yes':
                count = simulation_service.clear_simulated_sales()
                print(f"\n✅ Removed {count} simulated sales!")
            else:
                print("\n  Cancelled.")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            break

def admin_dashboard(controller: OrderController):
    clear_screen()
    print_header("🔐 SECURE ADMIN TERMINAL")
    
    # Use authentication service
    auth_service = AuthService()
    username = input("  ➤ Username: ")
    password = getpass.getpass("  ➤ Password: ")
    success, message = auth_service.login(username, password)
    
    if not success:
        print(f"\n❌ {message}")
        time.sleep(2)
        return

    client_service = ClientService()
    pricing_service = PricingConfigService()
    simulation_service = SimulationService()

    while True:
        clear_screen()
        summary = controller.get_financial_summary()
        print_header("📈 BANANAI EMPIRE COMMAND CENTER")
        
        # Proactive Logistics Monitoring
        alerts = InventoryManager.get_restock_report(controller.inventory)
        if alerts:
            print(" ⚠️  LOGISTICS ALERTS:")
            for a in alerts: print(f"    • {a}")
            print("─" * 70)

        # Financial Dashboard
        print(f"  REVENUE (TD): ${summary['revenue']:,.2f}")
        print(f"  PROFIT  (TD): ${summary['profit']:,.2f}")
        print(f"  VOLUME  (TD): {summary['orders']} Shipments")
        print("─" * 70)
        
        print("\n  [1] Open Master Ledger")
        print("  [2] Run Batch Janitor (Archive Empty)")
        print("  [3] Client Management")
        print("  [4] Pricing Configuration")
        print("  [5] Sales Management")
        print("  [6] Shipment Management")
        print("  [7] Historical Sales Simulation")
        print("  [8] Log Out")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            clear_screen()
            print_header("📜 MASTER SALES LEDGER")
            history = controller._read_history()
            if not history:
                print("\n  [!] Ledger is empty.")
            else:
                print(f"{'DATE' :<16} | {'ID' :<12} | {'DEST' :<10} | {'CLIENT' :<12} | {'PROFIT'}")
                print("─" * 80)
                for order in history[-50:]:  # Show last 50
                    client_id = order.get('client_id', 'N/A')
                    print(f"{order['timestamp'][:16]} | {order['order_id']} | "
                          f"{order['destination']:<10} | {client_id:<12} | ${order['net_profit']:>10,.2f}")
            input("\nPress Enter to go back...")
            
        elif choice == "2":
            count = InventoryManager.archive_empty_batches()
            print(f"\n✅ CLEANUP: {count} depleted batches moved to archive.")
            controller.inventory.batches = controller.batch_repo.load_all_batches()
            time.sleep(1.5)
        
        elif choice == "3":
            manage_clients(client_service)
        
        elif choice == "4":
            manage_pricing(pricing_service)
        
        elif choice == "5":
            manage_sales(controller)
        
        elif choice == "6":
            clear_screen()
            print_header("🚚 SHIPMENT MANAGEMENT")
            history = controller._read_history()
            if history:
                shipments = [h for h in history]
                total_weight = sum(s.get('weight_kg', 0) for s in shipments)
                total_shipping_cost = sum(s.get('shipping_cost', 0) for s in shipments)
                print(f"\n  Total Shipments: {len(shipments)}")
                print(f"  Total Weight: {total_weight:,.2f} kg")
                print(f"  Total Shipping Cost: ${total_shipping_cost:,.2f}")
                print(f"\n{'DATE' :<16} | {'ID' :<12} | {'DEST' :<10} | {'WEIGHT' :<10} | {'COST'}")
                print("─" * 70)
                for s in shipments[-30:]:  # Show last 30
                    print(f"{s['timestamp'][:16]} | {s['order_id']} | "
                          f"{s['destination']:<10} | {s['weight_kg']:>8.2f}kg | ${s['shipping_cost']:>8,.2f}")
            else:
                print("\n  [!] No shipments found.")
            input("\nPress Enter to go back...")
        
        elif choice == "7":
            manage_simulation(simulation_service, controller)
            
        elif choice == "8":
            break

def main():
    # Persistent Auth Loop
    username = login_register()
    
    # Infrastructure Setup
    repo = BatchRepository()
    inventory = Inventory()
    
    # Rehydrate Memory
    for b in repo.load_all_batches():
        inventory.add_batch(b)
        
    controller = OrderController(inventory, repo)

    while True:
        clear_screen()
        print_header("🍌 BANANAI GLOBAL BROKERAGE TERMINAL")
        print(f"  Logged in as: {username}")
        
        stock = inventory.get_total_stock_kg()
        status_tag = " [OK]" if stock > 5000 else " [LOW]"
        print(f"  LIVE WAREHOUSE STOCK: {stock:,.1f} kg {status_tag}")
        print("─" * 70)
        
        print("\n  [1] Buyer Portal (Client Sales)")
        print("  [2] Admin Terminal (Logistics & Profit)")
        print("  [3] Logout")
        print("  [4] System Shutdown")
        
        choice = input("\n  ➤ Main Selection: ")
        
        if choice == "1":
            buyer_portal(controller)
        elif choice == "2":
            admin_dashboard(controller)
        elif choice == "3":
            print("\n[SYSTEM] Logging out...")
            time.sleep(1)
            # Re-run auth to get a new username (or exit)
            username = login_register() 
        elif choice == "4":
            print("\n[SYSTEM] Powering down... Terminal closed.")
            break

if __name__ == "__main__":
    main()