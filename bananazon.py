import os
import time
import getpass
from typing import Dict, Any
from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory
from src.controller.order_controller import OrderController
from src.services.inventory_manager import InventoryManager

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

    invoice = controller.generate_invoice(selected_batch, weight, dest, tier)

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

def admin_dashboard(controller: OrderController):
    clear_screen()
    print_header("🔐 SECURE ADMIN TERMINAL")
    
    pw = getpass.getpass("  ➤ System Password: ")
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
        print("  [3] Log Out")
        
        choice = input("\n  ➤ Selection: ")
        
        if choice == "1":
            clear_screen()
            print_header("📜 MASTER SALES LEDGER")
            history = controller._read_history()
            if not history:
                print("\n  [!] Ledger is empty.")
            else:
                print(f"{'DATE' :<16} | {'ID' :<10} | {'DEST' :<10} | {'PROFIT'}")
                print("─" * 70)
                for order in history:
                    print(f"{order['timestamp'][:16]} | {order['order_id']} | {order['destination']:<10} | ${order['net_profit']:>10,.2f}")
            input("\nPress Enter to go back...")
            
        elif choice == "2":
            count = InventoryManager.archive_empty_batches()
            print(f"\n✅ CLEANUP: {count} depleted batches moved to archive.")
            # Critical: Refresh live inventory
            controller.inventory.batches = controller.batch_repo.load_all_batches()
            time.sleep(1.5)
            
        elif choice == "3":
            break

def main():
    repo = BatchRepository()
    inventory = Inventory()
    
    # Rehydrate Memory
    for b in repo.load_all_batches():
        inventory.add_batch(b)
        
    controller = OrderController(inventory, repo)

    while True:
        clear_screen()
        print_header("🍌 BANANAI GLOBAL BROKERAGE TERMINAL")
        
        stock = inventory.get_total_stock_kg()
        status_tag = " [OK]" if stock > 5000 else " [LOW]"
        print(f"  LIVE WAREHOUSE STOCK: {stock:,.1f} kg {status_tag}")
        print("─" * 70)
        
        print("\n  [1] Buyer Portal (Client Sales)")
        print("  [2] Admin Terminal (Logistics & Profit)")
        print("  [3] System Shutdown")
        
        choice = input("\n  ➤ Main Selection: ")
        
        if choice == "1":
            buyer_portal(controller)
        elif choice == "2":
            admin_dashboard(controller)
        elif choice == "3":
            print("\n[SYSTEM] Powering down... Terminal closed.")
            break

if __name__ == "__main__":
    main()