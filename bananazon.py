import os
import time
import getpass
from typing import Dict, Any
from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory
from src.controller.order_controller import OrderController
from src.services.inventory_manager import InventoryManager

def clear_screen():
    """Wipes terminal for a clean UI experience."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Standardized Branding for the Empire."""
    print("=" * 66)
    print(f"║ {title:^62} ║")
    print("=" * 66)

def buyer_portal(controller: OrderController):
    clear_screen()
    print_header("🍌 BANANAI BUYER PORTAL | GLOBAL LOGISTICS")
    
    # 1. Logistics Input
    print("\n[ Step 1: Destination & Volume ]")
    dest = input("Destination (USA/Germany/Spain/China/Local): ").upper() or "LOCAL"
    try:
        weight_input = input("Quantity needed (kg): ")
        weight = float(weight_input) if weight_input else 0.0
    except ValueError:
        print("❌ Error: Mass must be a numeric value.")
        time.sleep(1.5)
        return

    # 2. Quality Filter
    print("\n[ Step 2: Quality Preference ]")
    print("Options: [P]remium (0.65+) | [S]tandard (0.45+) | [E]conomic (Any)")
    tier_choice = input("Tier Choice: ").lower()
    tier = "premium" if tier_choice == 'p' else "economic" if tier_choice == 'e' else "standard"

    # 3. Matchmaking Engine
    proposals = controller.get_proposals(dest, weight, tier)
    matches = proposals['perfect'] + proposals['alternatives']
    
    if not matches:
        print("\n[!] CRITICAL: No viable stock found for this route/tier.")
        input("\nPress Enter to return...")
        return

    print(f"\n{'ID' :<4} | {'Batch ID' :<10} | {'Quality' :<8} | {'Life' :<5} | {'Availability'}")
    print("-" * 66)
    for i, b in enumerate(matches, 1):
        status = "PERFECT" if b in proposals['perfect'] else "ALT"
        print(f"[{i:02}] | {b.batch_id:<10} | {b.average_quality():.2f} ({status}) | {b.estimated_shelf_life_days()}d | {b.remaining_weight_kg:,.1f}kg")

    # 4. Transaction Initialization
    try:
        selection = input("\nSelect Option # to generate Manifest (0 to cancel): ")
        if not selection.isdigit() or int(selection) == 0: return
        selected_batch = matches[int(selection)-1]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    invoice = controller.generate_invoice(selected_batch, weight, dest, tier)

    # 5. The eBOL Preview
    clear_screen()
    print_header("🧾 GLOBAL SHIPPING MANIFEST (PREVIEW)")
    print(f"ORDER REF:    {invoice['order_id']}")
    print(f"COMMODITY:    Cavendish ({invoice['tier_sold']} Grade)")
    print(f"DESTINATION:  {invoice['destination']}")
    print(f"NET WEIGHT:   {invoice['weight_kg']:,} kg")
    print("-" * 66)
    print(f"UNIT PRICE:   ${invoice['unit_price']:.2f} USD/kg")
    print(f"TOTAL REVENUE: ${invoice['total_revenue']:,.2f} USD")
    print(f"NET PROFIT:   ${invoice['net_profit']:,.2f} USD")
    print("-" * 66)

    confirm = input("Confirm payment and book shipment? (y/n): ").lower()
    if confirm == 'y':
        success = controller.commit_transaction(invoice, selected_batch)
        if success:
            print("\n✅ TRANSACTION SUCCESS. Electronic Bill of Lading (eBOL) issued.")
            print(f"Manifest saved to: data/orders/physical_receipts/")
        else:
            print("\n❌ TRANSACTION FAILED: Stock depletion or ledger write error.")
    
    input("\nPress Enter to return...")

def admin_dashboard(controller: OrderController):
    clear_screen()
    print_header("🔐 SECURE ADMIN TERMINAL")
    
    # SECURITY FEATURE: getpass hides characters while typing
    print("[SYSTEM] Authentication required. Typing will be invisible.")
    pw = getpass.getpass("Admin Password: ")
    
    if pw != "zak123!":
        print("\n❌ ACCESS DENIED: UNAUTHORIZED ATTEMPT LOGGED.")
        time.sleep(2)
        return

    while True:
        clear_screen()
        summary = controller.get_financial_summary()
        print_header("📈 BANANAI EMPIRE COMMAND CENTER")
        
        # Proactive Logistics Monitoring
        alerts = InventoryManager.get_restock_report(controller.inventory)
        if alerts:
            print("🔔 SYSTEM ALERTS:")
            for a in alerts: print(f"  • {a}")
            print("-" * 66)

        print(f"CUMULATIVE REVENUE: ${summary['revenue']:,.2f}")
        print(f"CUMULATIVE PROFIT:  ${summary['profit']:,.2f}")
        print(f"TOTAL SHIPMENTS:    {summary['orders']}")
        print("-" * 66)
        
        print("\n[1] View Sales Ledger")
        print("[2] Archive Depleted Batches (Janitor)")
        print("[3] Log Out")
        
        choice = input("\nAdmin Selection > ")
        
        if choice == "1":
            clear_screen()
            print_header("📜 MASTER SALES LEDGER")
            history = controller._read_history()
            if not history:
                print("\n[!] Ledger is currently empty.")
            else:
                for order in history:
                    print(f"{order['timestamp'][:16]} | {order['order_id']} | {order['destination']:<8} | Profit: ${order['net_profit']:>10,.2f}")
            input("\nPress Enter...")
            
        elif choice == "2":
            count = InventoryManager.archive_empty_batches()
            print(f"\n✅ Clean-up complete: {count} empty files moved to archive.")
            # Refresh live memory from disk
            controller.inventory.batches = controller.batch_repo.load_all_batches()
            time.sleep(1.5)
            
        elif choice == "3":
            break

def main():
    # Persistence Layer Initialization
    repo = BatchRepository()
    inventory = Inventory()
    
    # Rehydrate Memory
    for b in repo.load_all_batches():
        inventory.add_batch(b)
        
    controller = OrderController(inventory, repo)

    while True:
        clear_screen()
        print_header("🍌 BANANAI GLOBAL BROKERAGE TERMINAL")
        print(f"LIVE WAREHOUSE STOCK: {inventory.get_total_stock_kg():,.1f} kg")
        print("\n[1] Buyer Portal (Global Export)")
        print("[2] Admin Dashboard (Financials)")
        print("[3] System Shutdown")
        
        choice = input("\nSelection > ")
        
        if choice == "1":
            buyer_portal(controller)
        elif choice == "2":
            admin_dashboard(controller)
        elif choice == "3":
            print("\n[SYSTEM] Terminating connection. Safe travels, broker.")
            break

if __name__ == "__main__":
    main()