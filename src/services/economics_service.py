class EconomicsService:
    PRICE_PER_KG = 1.25       # adjust later
    LOGISTICS_COST_PER_KG = 0.30

    @staticmethod
    def estimate(batch, simulated_qty: int) -> dict:
        avg_weight_g = batch.average_weight()
        total_weight_kg = (avg_weight_g * simulated_qty) / 1000

        avg_quality = batch.average_quality()
        shelf_life = batch.estimated_shelf_life_days()

        # Quality discount
        quality_factor = min(avg_quality, 1.0)

        # Spoilage risk
        loss_pct = 0.05 if shelf_life >= 5 else 0.15 if shelf_life >= 3 else 0.30

        revenue = total_weight_kg * EconomicsService.PRICE_PER_KG * quality_factor
        logistics = total_weight_kg * EconomicsService.LOGISTICS_COST_PER_KG
        loss = revenue * loss_pct

        profit = revenue - logistics - loss

        return {
            "total_weight_kg": round(total_weight_kg, 2),
            "estimated_revenue": round(revenue, 2),
            "estimated_loss": round(loss, 2),
            "logistics_cost": round(logistics, 2),
            "net_profit": round(profit, 2),
            "loss_pct": int(loss_pct * 100)
        }
