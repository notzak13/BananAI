# src/services/order_manager.py
import uuid
from datetime import datetime
from src.services.huggingface_service import OpenAIService
from src.repository.batch_repository import BatchRepository


class OrderManager:

    def __init__(self):
        self.batch_repo = BatchRepository()
        self.orders = []

    def create_order(self, destination: str, weight_kg: float, quality_tier: str):
        # Load all batches
        batches = self.batch_repo.load_all_batches()
        if not batches:
            raise ValueError("No batches available in inventory")

        # For simplicity, pick the first batch with enough stock and closest quality
        batch = next(
            (b for b in batches if b.remaining_weight_g >= weight_kg * 1000),
            None
        )
        if not batch:
            raise ValueError("No batch can fulfill this order")

        batch_info = batch.to_dict()
        order_request = {
            "destination": destination,
            "weight_kg": weight_kg,
            "quality_tier": quality_tier
        }

        # Ask GPT-3.5 for dynamic info
        dynamic_info = OpenAIService.get_dynamic_order_info(batch_info, order_request)

        # Show info to user and ask accept/decline
        print("\n=== ORDER DETAILS ===")
        print(json.dumps(dynamic_info, indent=2))
        decision = input("Do you accept this order? (yes/no): ").strip().lower()
        if decision != "yes":
            print("[DECLINED] Order not placed.")
            return None

        # Fulfill order
        batch.consume(weight_kg * 1000)
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "destination": destination,
            "weight_g": weight_kg * 1000,
            "quality_tier": quality_tier,
            "status": "fulfilled",
            "fulfilled_batches": [batch.batch_id],
            "created_at": datetime.utcnow().isoformat(),
            **dynamic_info
        }

        self.orders.append(order)
        print(f"[FULFILLED] Order {order_id} saved.")
        return order
